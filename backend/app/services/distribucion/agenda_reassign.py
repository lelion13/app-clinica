"""Reassign / unassign (id_agenda, weekday) → room with hours + overlap validation (Agenda DnD)."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, time

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.consulting_room import ConsultingRoom, ConsultingRoomIdAgenda, RoomOperatingHour
from app.models.ocupacion import OcupacionHorarioActivo
from app.schemas.distribucion import AgendaReassignResponse
from app.services import room_agenda_map as map_svc
from app.services.distribucion import agenda_ocupacion as agenda_svc

WEEKDAY_JS_LABEL = {
    0: "domingo",
    1: "lunes",
    2: "martes",
    3: "miércoles",
    4: "jueves",
    5: "viernes",
    6: "sábado",
}


def _time_to_minutes(t: time) -> int:
    return t.hour * 60 + t.minute + t.second // 60


def _merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not intervals:
        return []
    ordered = sorted(intervals)
    merged: list[tuple[int, int]] = [ordered[0]]
    for start, end in ordered[1:]:
        last_s, last_e = merged[-1]
        if start <= last_e:
            merged[-1] = (last_s, max(last_e, end))
        else:
            merged.append((start, end))
    return merged


def _interval_covered(start: int, end: int, hours: list[tuple[int, int]]) -> bool:
    """True if [start, end) fits entirely inside one merged hours segment."""
    if end <= start:
        return False
    for hs, he in _merge_intervals(hours):
        if hs <= start and end <= he:
            return True
    return False


def _intervals_overlap(a0: int, a1: int, b0: int, b1: int) -> bool:
    """Half-open [a0,a1) vs [b0,b1). Adjacent (a1==b0) is NOT overlap."""
    return a0 < b1 and b0 < a1


def _py_weekday_to_js(py_weekday: int) -> int:
    return (py_weekday + 1) % 7


def _fmt_hm(minutes: int) -> str:
    h, m = divmod(minutes, 60)
    return f"{h:02d}:{m:02d}"


def _intervals_for_id_agenda(db: Session, id_agenda: int) -> dict[int, list[tuple[int, int, str]]]:
    """js_weekday → list of (start_min, end_min, dia_label)."""
    rows = db.execute(select(OcupacionHorarioActivo)).scalars().all()
    by_wd: dict[int, list[tuple[int, int, str]]] = defaultdict(list)
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
        js_wd = _py_weekday_to_js(py_wd)
        dia_label = (fields["dia"] or WEEKDAY_JS_LABEL.get(js_wd, str(js_wd))).strip()
        by_wd[js_wd].append((_time_to_minutes(h_desde), _time_to_minutes(h_hasta), dia_label))
    return by_wd


def _hours_for_room(db: Session, room_id: int) -> dict[int, list[tuple[int, int]]]:
    rows = list(
        db.execute(
            select(RoomOperatingHour).where(
                RoomOperatingHour.deleted_at.is_(None),
                RoomOperatingHour.room_id == room_id,
            )
        )
        .scalars()
        .all()
    )
    by_wd: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for h in rows:
        start = _time_to_minutes(h.start_time)
        end = _time_to_minutes(h.end_time)
        if end <= start:
            continue
        by_wd[int(h.weekday)].append((start, end))
    return by_wd


def _other_agenda_intervals_on_room(
    db: Session,
    room_id: int,
    *,
    exclude_id_agenda: int,
    exclude_weekday: int,
) -> dict[int, list[tuple[int, int, int]]]:
    """js_weekday → (start, end, other_id_agenda) for agendas mapped to room that weekday."""
    maps = list(db.execute(select(ConsultingRoomIdAgenda)).scalars().all())
    mapped_keys = {
        (m.id_agenda, int(m.weekday))
        for m in maps
        if m.room_id == room_id and not (m.id_agenda == exclude_id_agenda and int(m.weekday) == exclude_weekday)
    }
    if not mapped_keys:
        return {}

    rows = db.execute(select(OcupacionHorarioActivo)).scalars().all()
    by_wd: dict[int, list[tuple[int, int, int]]] = defaultdict(list)
    for row in rows:
        fields = agenda_svc._payload_fields(row)
        id_ag = fields["id_agenda"]
        if id_ag is None:
            continue
        py_wd = agenda_svc._weekday_from_dia(fields["dia"])
        if py_wd is None:
            continue
        h_desde = agenda_svc._parse_hora(fields["hora_desde"])
        h_hasta = agenda_svc._parse_hora(fields["hora_hasta"])
        if h_desde is None or h_hasta is None or h_hasta <= h_desde:
            continue
        js_wd = _py_weekday_to_js(py_wd)
        if (int(id_ag), js_wd) not in mapped_keys:
            continue
        by_wd[js_wd].append((_time_to_minutes(h_desde), _time_to_minutes(h_hasta), int(id_ag)))
    return by_wd


def validate_assign_weekday(db: Session, id_agenda: int, room_id: int, weekday: int) -> None:
    """Validate hours + overlap for a single JS weekday. Raises HTTPException on failure."""
    if weekday < 0 or weekday > 6:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="weekday inválido")

    agenda_by_wd = _intervals_for_id_agenda(db, id_agenda)
    intervals = agenda_by_wd.get(weekday)
    if not intervals:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": f"La agenda no tiene bloques válidos el {WEEKDAY_JS_LABEL.get(weekday, weekday)}",
                "id_agenda": id_agenda,
                "weekday": weekday,
                "code": "no_sync_blocks",
            },
        )

    hours_by_wd = _hours_for_room(db, room_id)
    others_by_wd = _other_agenda_intervals_on_room(
        db, room_id, exclude_id_agenda=id_agenda, exclude_weekday=weekday
    )
    conflicts: list[dict] = []
    box_hours = hours_by_wd.get(weekday, [])
    others = others_by_wd.get(weekday, [])

    for start, end, dia_label in intervals:
        if not _interval_covered(start, end, box_hours):
            conflicts.append(
                {
                    "type": "outside_hours",
                    "weekday": weekday,
                    "dia": dia_label,
                    "hora_desde": _fmt_hm(start),
                    "hora_hasta": _fmt_hm(end),
                    "message": (
                        f"Fuera del horario del consultorio el {dia_label} "
                        f"({_fmt_hm(start)}–{_fmt_hm(end)})"
                    ),
                }
            )
            continue
        for o_start, o_end, other_id in others:
            if _intervals_overlap(start, end, o_start, o_end):
                conflicts.append(
                    {
                        "type": "overlap",
                        "weekday": weekday,
                        "dia": dia_label,
                        "hora_desde": _fmt_hm(start),
                        "hora_hasta": _fmt_hm(end),
                        "conflict_id_agenda": other_id,
                        "conflict_hora_desde": _fmt_hm(o_start),
                        "conflict_hora_hasta": _fmt_hm(o_end),
                        "message": (
                            f"Solapa con agenda {other_id} el {dia_label} "
                            f"({_fmt_hm(start)}–{_fmt_hm(end)} vs {_fmt_hm(o_start)}–{_fmt_hm(o_end)})"
                        ),
                    }
                )

    if conflicts:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": conflicts[0]["message"],
                "id_agenda": id_agenda,
                "weekday": weekday,
                "target_room_id": room_id,
                "code": "validation_failed",
                "conflicts": conflicts,
            },
        )


def reassign_agenda(
    db: Session,
    *,
    id_agenda: int,
    weekday: int,
    target_room_id: int | None,
    actor_id: int,
    confirm_move: bool = False,
    confirm_unassign: bool = False,
) -> AgendaReassignResponse:
    if id_agenda <= 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="id_agenda inválido")
    if weekday < 0 or weekday > 6:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="weekday inválido")

    existing = db.execute(
        select(ConsultingRoomIdAgenda).where(
            ConsultingRoomIdAgenda.id_agenda == id_agenda,
            ConsultingRoomIdAgenda.weekday == weekday,
        )
    ).scalar_one_or_none()

    # --- Unassign ---
    if target_room_id is None:
        if not confirm_unassign:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "Confirmá la desasignación del consultorio para este día",
                    "id_agenda": id_agenda,
                    "weekday": weekday,
                    "requires_confirm_unassign": True,
                    "code": "requires_confirm_unassign",
                },
            )
        if existing:
            db.delete(existing)
            db.commit()
        return AgendaReassignResponse(
            id_agenda=id_agenda, weekday=weekday, room_id=None, room_code=None
        )

    # --- Assign / move ---
    room = map_svc._ensure_room(db, target_room_id)

    if existing and existing.room_id == target_room_id:
        return AgendaReassignResponse(
            id_agenda=id_agenda, weekday=weekday, room_id=room.id, room_code=room.code
        )

    if existing and existing.room_id != target_room_id and not confirm_move:
        other = db.execute(
            select(ConsultingRoom).where(ConsultingRoom.id == existing.room_id)
        ).scalar_one_or_none()
        code = other.code if other else str(existing.room_id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": (
                    f"Esta agenda el {WEEKDAY_JS_LABEL.get(weekday, weekday)} está en {code}. "
                    f"¿Moverla a {room.code}?"
                ),
                "id_agenda": id_agenda,
                "weekday": weekday,
                "current_room_id": existing.room_id,
                "current_room_code": code,
                "target_room_id": room.id,
                "target_room_code": room.code,
                "requires_confirm_move": True,
                "code": "requires_confirm_move",
            },
        )

    validate_assign_weekday(db, id_agenda, target_room_id, weekday)

    now = datetime.utcnow()
    if existing:
        existing.room_id = target_room_id
        existing.updated_at = now
        existing.updated_by = actor_id
    else:
        db.add(
            ConsultingRoomIdAgenda(
                id_agenda=id_agenda,
                weekday=weekday,
                room_id=target_room_id,
                created_at=now,
                updated_at=now,
                created_by=actor_id,
                updated_by=actor_id,
            )
        )
    db.commit()
    return AgendaReassignResponse(
        id_agenda=id_agenda, weekday=weekday, room_id=room.id, room_code=room.code
    )
