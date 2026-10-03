"""Mapeo id_agenda (ocupacion sync) → consulting_rooms."""

from __future__ import annotations

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


def _label_for_id_agenda(db: Session, id_agenda: int) -> str:
    rows = db.execute(select(OcupacionHorarioActivo)).scalars().all()
    for row in rows:
        raw = row.payload if isinstance(row.payload, dict) else {}
        if _id_agenda_from_payload(raw) == id_agenda:
            nombre = _nombre_agenda_from_payload(raw) or _as_str(raw.get("medico")) or ""
            return f"{id_agenda} — {nombre}".rstrip(" —")
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
            .order_by(ConsultingRoomIdAgenda.id_agenda)
        )
        .scalars()
        .all()
    )
    items = [
        RoomIdAgendaItem(id_agenda=m.id_agenda, label=_label_for_id_agenda(db, m.id_agenda)) for m in maps
    ]
    return RoomIdAgendaListResponse(items=items)


def add_room_id_agenda(
    db: Session,
    room_id: int,
    id_agenda: int,
    *,
    actor_id: int,
    confirm_move: bool = False,
) -> RoomIdAgendaItem:
    _ensure_room(db, room_id)
    if id_agenda <= 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="id_agenda inválido")

    existing = db.execute(
        select(ConsultingRoomIdAgenda).where(ConsultingRoomIdAgenda.id_agenda == id_agenda)
    ).scalar_one_or_none()
    now = datetime.utcnow()

    if existing:
        if existing.room_id == room_id:
            return RoomIdAgendaItem(id_agenda=id_agenda, label=_label_for_id_agenda(db, id_agenda))
        if not confirm_move:
            other = db.execute(
                select(ConsultingRoom).where(ConsultingRoom.id == existing.room_id)
            ).scalar_one_or_none()
            code = other.code if other else str(existing.room_id)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "id_agenda ya está asociado a otro consultorio",
                    "id_agenda": id_agenda,
                    "current_room_id": existing.room_id,
                    "current_room_code": code,
                    "requires_confirm_move": True,
                },
            )
        existing.room_id = room_id
        existing.updated_at = now
        existing.updated_by = actor_id
        db.commit()
        return RoomIdAgendaItem(id_agenda=id_agenda, label=_label_for_id_agenda(db, id_agenda))

    item = ConsultingRoomIdAgenda(
        id_agenda=id_agenda,
        room_id=room_id,
        created_at=now,
        updated_at=now,
        created_by=actor_id,
        updated_by=actor_id,
    )
    db.add(item)
    db.commit()
    return RoomIdAgendaItem(id_agenda=id_agenda, label=_label_for_id_agenda(db, id_agenda))


def remove_room_id_agenda(db: Session, room_id: int, id_agenda: int) -> None:
    _ensure_room(db, room_id)
    item = db.execute(
        select(ConsultingRoomIdAgenda).where(
            ConsultingRoomIdAgenda.room_id == room_id,
            ConsultingRoomIdAgenda.id_agenda == id_agenda,
        )
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asociación no encontrada")
    db.delete(item)
    db.commit()


def replace_room_id_agendas(
    db: Session,
    room_id: int,
    items: list[RoomIdAgendaReplaceItem],
    *,
    actor_id: int,
) -> RoomIdAgendaListResponse:
    """Replace the set of id_agenda mappings for a room in one transaction."""
    _ensure_room(db, room_id)

    desired: list[tuple[int, bool]] = []
    seen: set[int] = set()
    for raw in items:
        id_agenda = int(raw.id_agenda)
        confirm_move = bool(raw.confirm_move)
        if id_agenda <= 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="id_agenda inválido")
        if id_agenda in seen:
            continue
        seen.add(id_agenda)
        desired.append((id_agenda, confirm_move))

    all_maps = list(db.execute(select(ConsultingRoomIdAgenda)).scalars().all())
    by_agenda = {m.id_agenda: m for m in all_maps}

    for id_agenda, confirm_move in desired:
        existing = by_agenda.get(id_agenda)
        if existing and existing.room_id != room_id and not confirm_move:
            other = db.execute(
                select(ConsultingRoom).where(ConsultingRoom.id == existing.room_id)
            ).scalar_one_or_none()
            code = other.code if other else str(existing.room_id)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "id_agenda ya está asociado a otro consultorio",
                    "id_agenda": id_agenda,
                    "current_room_id": existing.room_id,
                    "current_room_code": code,
                    "requires_confirm_move": True,
                },
            )

    now = datetime.utcnow()
    desired_ids = {id_agenda for id_agenda, _ in desired}

    try:
        for m in all_maps:
            if m.room_id == room_id and m.id_agenda not in desired_ids:
                db.delete(m)

        for id_agenda, confirm_move in desired:
            existing = by_agenda.get(id_agenda)
            if existing:
                if existing.room_id != room_id:
                    existing.room_id = room_id
                    existing.updated_at = now
                    existing.updated_by = actor_id
            else:
                db.add(
                    ConsultingRoomIdAgenda(
                        id_agenda=id_agenda,
                        room_id=room_id,
                        created_at=now,
                        updated_at=now,
                        created_by=actor_id,
                        updated_by=actor_id,
                    )
                )
        db.commit()
    except HTTPException:
        db.rollback()
        raise
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
        # medico also derived column
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
    room_ids = {m.room_id for m in maps}
    rooms_by_id: dict[int, ConsultingRoom] = {}
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
    map_by_agenda = {m.id_agenda: m.room_id for m in maps}

    items: list[AgendaLookupItem] = []
    for k in sorted(by_agenda.keys()):
        data = dict(by_agenda[k])
        rid = map_by_agenda.get(k)
        room = rooms_by_id.get(rid) if rid is not None else None
        if room is not None:
            data["current_room_id"] = room.id
            data["current_room_code"] = room.code
        else:
            data["current_room_id"] = None
            data["current_room_code"] = None
        items.append(AgendaLookupItem(**data))
    return AgendaLookupResponse(items=items)


def agenda_to_room_map(db: Session) -> dict[int, int]:
    rows = db.execute(select(ConsultingRoomIdAgenda)).scalars().all()
    return {r.id_agenda: r.room_id for r in rows}
