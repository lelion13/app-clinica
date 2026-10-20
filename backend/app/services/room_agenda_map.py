"""Mapeo (id_agenda, weekday) → consulting_rooms."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.consulting_room import ConsultingRoom, ConsultingRoomIdAgenda
from app.models.ocupacion import OcupacionHorarioActivo
from app.schemas.consulting_room import (
    AgendaLookupItem,
    AgendaLookupResponse,
    RoomIdAgendaItem,
    RoomIdAgendaListResponse,
    RoomIdAgendaReplaceItem,
)
from app.services.distribucion import agenda_ocupacion as agenda_svc
from app.services.distribucion import agenda_reassign as reassign_svc

WEEKDAY_JS_LABEL = {
    0: "domingo",
    1: "lunes",
    2: "martes",
    3: "miércoles",
    4: "jueves",
    5: "viernes",
    6: "sábado",
}


def _as_str(value) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    return s or None


def _nombre_agenda_from_payload(raw: dict) -> str | None:
    return _as_str(raw.get("nombre_agenda"))


def _id_agenda_from_payload(raw: dict) -> int | None:
    value = raw.get("id_agenda")
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _py_weekday_to_js(py_weekday: int) -> int:
    return (py_weekday + 1) % 7


def sync_weekdays_for_id_agenda(db: Session, id_agenda: int) -> set[int]:
    """JS weekdays with parseable sync blocks for id_agenda."""
    rows = db.execute(select(OcupacionHorarioActivo)).scalars().all()
    out: set[int] = set()
    for row in rows:
        fields = agenda_svc._payload_fields(row)
        if fields["id_agenda"] != id_agenda:
            continue
        py_wd = agenda_svc._weekday_from_dia(fields["dia"])
        if py_wd is None:
            continue
        h_desde = agenda_svc._parse_hora(fields["hora_desde"])
        h_hasta = agenda_svc._parse_hora(fields["hora_hasta"])
        if h_desde is None or h_hasta is None or h_hasta <= h_desde:
            continue
        out.add(_py_weekday_to_js(py_wd))
    return out


def _base_label_for_id_agenda(db: Session, id_agenda: int) -> str:
    rows = db.execute(select(OcupacionHorarioActivo)).scalars().all()
    for row in rows:
        raw = row.payload if isinstance(row.payload, dict) else {}
        if _id_agenda_from_payload(raw) == id_agenda:
            nombre = _nombre_agenda_from_payload(raw) or _as_str(raw.get("medico")) or ""
            return f"{id_agenda} — {nombre}".rstrip(" —") if nombre else str(id_agenda)
    return str(id_agenda)


def _ensure_room(db: Session, room_id: int) -> ConsultingRoom:
    room = db.execute(
        select(ConsultingRoom).where(ConsultingRoom.id == room_id, ConsultingRoom.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultorio no encontrado")
    return room


def list_room_id_agendas(db: Session, room_id: int) -> RoomIdAgendaListResponse:
    _ensure_room(db, room_id)
    maps = (
        db.execute(
            select(ConsultingRoomIdAgenda)
            .where(ConsultingRoomIdAgenda.room_id == room_id)
            .order_by(ConsultingRoomIdAgenda.id_agenda, ConsultingRoomIdAgenda.weekday)
        )
        .scalars()
        .all()
    )
    by_agenda: dict[int, list[int]] = defaultdict(list)
    for m in maps:
        by_agenda[m.id_agenda].append(int(m.weekday))

    items: list[RoomIdAgendaItem] = []
    for id_agenda in sorted(by_agenda.keys()):
        room_wds = sorted(set(by_agenda[id_agenda]))
        sync_wds = sync_weekdays_for_id_agenda(db, id_agenda)
        base = _base_label_for_id_agenda(db, id_agenda)
        # Full: todos los días sync están en este room
        if sync_wds and sync_wds <= set(room_wds):
            items.append(
                RoomIdAgendaItem(
                    id_agenda=id_agenda,
                    label=base,
                    weekday=None,
                    weekdays=sorted(sync_wds),
                )
            )
        else:
            for wd in room_wds:
                dia = WEEKDAY_JS_LABEL.get(wd, str(wd))
                items.append(
                    RoomIdAgendaItem(
                        id_agenda=id_agenda,
                        label=f"{base} - {dia}",
                        weekday=wd,
                        weekdays=[wd],
                    )
                )
    return RoomIdAgendaListResponse(items=items)


def add_room_id_agenda(
    db: Session,
    room_id: int,
    id_agenda: int,
    *,
    actor_id: int,
    confirm_move: bool = False,
    weekday: int | None = None,
) -> RoomIdAgendaItem:
    """Assign unassigned sync weekdays (or one weekday) to room. Does not steal other rooms."""
    _ = confirm_move  # legacy; Consultorios no pisa otros rooms
    _ensure_room(db, room_id)
    if id_agenda <= 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="id_agenda inválido")

    sync_wds = sync_weekdays_for_id_agenda(db, id_agenda)
    if weekday is not None:
        if weekday not in sync_wds:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="La agenda no tiene ese día en el sync",
            )
        pending = {weekday}
    else:
        all_maps = list(db.execute(select(ConsultingRoomIdAgenda)).scalars().all())
        mapped = {int(m.weekday) for m in all_maps if m.id_agenda == id_agenda}
        pending = sync_wds - mapped

    if not pending:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "No hay días pendientes (Sin consultorio) para asociar",
                "id_agenda": id_agenda,
                "code": "no_pending_days",
            },
        )

    # Validate all pending first (all-or-nothing)
    conflicts: list[dict] = []
    for wd in sorted(pending):
        try:
            reassign_svc.validate_assign_weekday(db, id_agenda, room_id, wd)
        except HTTPException as exc:
            if isinstance(exc.detail, dict) and exc.detail.get("conflicts"):
                conflicts.extend(exc.detail["conflicts"])
            else:
                conflicts.append(
                    {
                        "type": "error",
                        "weekday": wd,
                        "message": str(exc.detail),
                    }
                )
    if conflicts:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": conflicts[0].get("message", "Conflicto al asociar"),
                "id_agenda": id_agenda,
                "target_room_id": room_id,
                "code": "validation_failed",
                "conflicts": conflicts,
            },
        )

    now = datetime.utcnow()
    for wd in sorted(pending):
        db.add(
            ConsultingRoomIdAgenda(
                id_agenda=id_agenda,
                weekday=wd,
                room_id=room_id,
                created_at=now,
                updated_at=now,
                created_by=actor_id,
                updated_by=actor_id,
            )
        )
    db.commit()

    listed = list_room_id_agendas(db, room_id)
    for item in listed.items:
        if item.id_agenda == id_agenda:
            return item
    return RoomIdAgendaItem(
        id_agenda=id_agenda,
        label=_base_label_for_id_agenda(db, id_agenda),
        weekday=None,
        weekdays=sorted(pending),
    )


def remove_room_id_agenda(
    db: Session,
    room_id: int,
    id_agenda: int,
    *,
    weekday: int | None = None,
) -> None:
    """Remove one weekday or all weekdays of id_agenda on this room."""
    _ensure_room(db, room_id)
    q = select(ConsultingRoomIdAgenda).where(
        ConsultingRoomIdAgenda.room_id == room_id,
        ConsultingRoomIdAgenda.id_agenda == id_agenda,
    )
    if weekday is not None:
        q = q.where(ConsultingRoomIdAgenda.weekday == weekday)
    items = list(db.execute(q).scalars().all())
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asociación no encontrada")
    for item in items:
        db.delete(item)
    db.commit()


def replace_room_id_agendas(
    db: Session,
    room_id: int,
    items: list[RoomIdAgendaReplaceItem],
    *,
    actor_id: int,
) -> RoomIdAgendaListResponse:
    """
    Diff-based replace for this room.

    Each item:
    - weekday set → keep/add that (id_agenda, weekday)
    - weekday null + weekdays non-empty → keep those weekdays (full row already on room)
    - weekday null + weekdays empty → treat as new: assign all currently unassigned sync days
    """
    _ensure_room(db, room_id)

    current_maps = list(
        db.execute(select(ConsultingRoomIdAgenda).where(ConsultingRoomIdAgenda.room_id == room_id))
        .scalars()
        .all()
    )
    current_pairs = {(m.id_agenda, int(m.weekday)) for m in current_maps}

    all_maps = list(db.execute(select(ConsultingRoomIdAgenda)).scalars().all())
    mapped_elsewhere: dict[tuple[int, int], int] = {
        (m.id_agenda, int(m.weekday)): m.room_id for m in all_maps if m.room_id != room_id
    }

    desired: set[tuple[int, int]] = set()
    new_assign_agendas: set[int] = set()

    for raw in items:
        id_agenda = int(raw.id_agenda)
        if id_agenda <= 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="id_agenda inválido")
        if raw.weekday is not None:
            desired.add((id_agenda, int(raw.weekday)))
        elif raw.weekdays:
            for wd in raw.weekdays:
                desired.add((id_agenda, int(wd)))
        else:
            # Nueva agenda desde lookup: solo días aún sin mapa en ningún room
            new_assign_agendas.add(id_agenda)

    for id_agenda in new_assign_agendas:
        sync_wds = sync_weekdays_for_id_agenda(db, id_agenda)
        mapped_any = {int(m.weekday) for m in all_maps if m.id_agenda == id_agenda}
        pending = sync_wds - mapped_any
        for wd in pending:
            desired.add((id_agenda, wd))

    to_remove = current_pairs - desired
    to_add = desired - current_pairs

    # No pisar días que están en otro room
    stolen = [pair for pair in to_add if pair in mapped_elsewhere]
    if stolen:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Hay días asociados a otro consultorio; no se mueven desde aquí",
                "code": "days_on_other_room",
                "pairs": [{"id_agenda": a, "weekday": w} for a, w in stolen],
            },
        )

    # Validar altas todo-o-nada
    conflicts: list[dict] = []
    for id_agenda, wd in sorted(to_add):
        try:
            reassign_svc.validate_assign_weekday(db, id_agenda, room_id, wd)
        except HTTPException as exc:
            if isinstance(exc.detail, dict) and exc.detail.get("conflicts"):
                conflicts.extend(exc.detail["conflicts"])
            else:
                conflicts.append({"type": "error", "weekday": wd, "id_agenda": id_agenda, "message": str(exc.detail)})
    if conflicts:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": conflicts[0].get("message", "Conflicto al asociar"),
                "code": "validation_failed",
                "conflicts": conflicts,
            },
        )

    now = datetime.utcnow()
    try:
        for m in current_maps:
            if (m.id_agenda, int(m.weekday)) in to_remove:
                db.delete(m)
        for id_agenda, wd in sorted(to_add):
            db.add(
                ConsultingRoomIdAgenda(
                    id_agenda=id_agenda,
                    weekday=wd,
                    room_id=room_id,
                    created_at=now,
                    updated_at=now,
                    created_by=actor_id,
                    updated_by=actor_id,
                )
            )
        db.commit()
    except Exception:
        db.rollback()
        raise

    return list_room_id_agendas(db, room_id)


def lookup_agendas_by_medico(db: Session, q: str, *, limit: int = 40) -> AgendaLookupResponse:
    needle = (q or "").strip().casefold()
    if len(needle) < 2:
        return AgendaLookupResponse(items=[])

    rows = db.execute(select(OcupacionHorarioActivo)).scalars().all()
    by_agenda: dict[int, dict] = {}
    for row in rows:
        raw = row.payload if isinstance(row.payload, dict) else {}
        id_agenda = _id_agenda_from_payload(raw)
        if id_agenda is None:
            continue
        medico = _as_str(raw.get("medico")) or ""
        medico_col = _as_str(row.medico) or ""
        haystack = f"{medico} {medico_col} {_nombre_agenda_from_payload(raw) or ''}".casefold()
        if needle not in haystack:
            continue
        if id_agenda in by_agenda:
            continue
        nombre = _nombre_agenda_from_payload(raw) or medico or medico_col or ""
        by_agenda[id_agenda] = {
            "id_agenda": id_agenda,
            "label": f"{id_agenda} — {nombre}".rstrip(" —"),
            "medico": medico or medico_col or None,
            "nombre_agenda": _nombre_agenda_from_payload(raw),
        }
        if len(by_agenda) >= limit:
            break

    maps = list(db.execute(select(ConsultingRoomIdAgenda)).scalars().all())
    rooms_by_id: dict[int, ConsultingRoom] = {}
    room_ids = {m.room_id for m in maps}
    if room_ids:
        room_rows = (
            db.execute(
                select(ConsultingRoom).where(
                    ConsultingRoom.id.in_(list(room_ids)),
                    ConsultingRoom.deleted_at.is_(None),
                )
            )
            .scalars()
            .all()
        )
        rooms_by_id = {r.id: r for r in room_rows}

    # current_room: solo si todos los días sync están en el mismo room
    maps_by_agenda: dict[int, list[ConsultingRoomIdAgenda]] = defaultdict(list)
    for m in maps:
        maps_by_agenda[m.id_agenda].append(m)

    items: list[AgendaLookupItem] = []
    for k in sorted(by_agenda.keys()):
        data = dict(by_agenda[k])
        sync_wds = sync_weekdays_for_id_agenda(db, k)
        agenda_maps = maps_by_agenda.get(k) or []
        room_ids_for = {m.room_id for m in agenda_maps}
        mapped_wds = {int(m.weekday) for m in agenda_maps}
        if sync_wds and sync_wds <= mapped_wds and len(room_ids_for) == 1:
            rid = next(iter(room_ids_for))
            room = rooms_by_id.get(rid)
            data["current_room_id"] = room.id if room else rid
            data["current_room_code"] = room.code if room else str(rid)
        else:
            data["current_room_id"] = None
            data["current_room_code"] = None
        items.append(AgendaLookupItem(**data))
    return AgendaLookupResponse(items=items)


def agenda_weekday_to_room_map(db: Session) -> dict[tuple[int, int], int]:
    """(id_agenda, js_weekday) → room_id."""
    rows = db.execute(select(ConsultingRoomIdAgenda)).scalars().all()
    return {(int(r.id_agenda), int(r.weekday)): int(r.room_id) for r in rows}


def agenda_to_room_map(db: Session) -> dict[int, int]:
    """Legacy: primer room_id por id_agenda (cualquier weekday). Preferir agenda_weekday_to_room_map."""
    rows = db.execute(select(ConsultingRoomIdAgenda)).scalars().all()
    out: dict[int, int] = {}
    for r in rows:
        if r.id_agenda not in out:
            out[int(r.id_agenda)] = int(r.room_id)
    return out
