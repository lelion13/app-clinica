"""Indicadores de ocupación: horas sync (agendas mapeadas) ÷ horario operativo del box."""

from __future__ import annotations

from datetime import date, datetime, time

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.calendar import weekday_js_from_date
from app.models.consulting_room import ConsultingRoom, RoomOperatingHour
from app.models.ocupacion import OcupacionHorarioActivo
from app.schemas.distribucion import IndicadoresOcupacionResponse, IndicadoresRoomRef
from app.services import room_agenda_map as room_agenda_map_service
from app.services.distribucion import agenda_ocupacion as agenda_svc


def _hours_between(start: time, end: time) -> float:
    if end <= start:
        return 0.0
    base = date(2000, 1, 1)
    return (datetime.combine(base, end) - datetime.combine(base, start)).total_seconds() / 3600.0


def _parse_date(raw: str) -> date:
    text = (raw or "").strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="date es obligatorio (YYYY-MM-DD)",
        )
    try:
        return date.fromisoformat(text[:10])
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="date con formato inválido (usar YYYY-MM-DD)",
        ) from exc


def _match_especialidad(esp: str | None, esp_agenda: str | None, selected: str | None) -> bool:
    if not selected:
        return True
    return agenda_svc._match_multi(esp, [selected]) or agenda_svc._match_multi(esp_agenda, [selected])


def _match_medico(medico: str | None, selected: str | None) -> bool:
    if not selected:
        return True
    return agenda_svc._match_multi(medico, [selected])


def compute_indicadores(
    db: Session,
    *,
    date_str: str,
    location_id: int | None = None,
    room_id: int | None = None,
    especialidad: str | None = None,
    medico: str | None = None,
) -> IndicadoresOcupacionResponse:
    day = _parse_date(date_str)
    py_weekday = day.weekday()  # lunes=0 … domingo=6 (match dia sync)
    js_weekday = weekday_js_from_date(day)

    q = select(ConsultingRoom).where(ConsultingRoom.deleted_at.is_(None)).order_by(ConsultingRoom.code)
    if location_id is not None:
        q = q.where(ConsultingRoom.location_id == location_id)
    if room_id is not None:
        q = q.where(ConsultingRoom.id == room_id)
    rooms = list(db.execute(q).scalars().all())
    room_ids = [r.id for r in rooms]

    agenda_rooms = room_agenda_map_service.agenda_to_room_map(db)
    room_agendas: dict[int, set[int]] = {}
    for id_agenda, rid in agenda_rooms.items():
        room_agendas.setdefault(rid, set()).add(id_agenda)

    hours_rows = []
    if room_ids:
        hours_rows = list(
            db.execute(
                select(RoomOperatingHour).where(
                    RoomOperatingHour.deleted_at.is_(None),
                    RoomOperatingHour.room_id.in_(room_ids),
                    RoomOperatingHour.weekday == js_weekday,
                )
            ).scalars().all()
        )
    enabled_by_room: dict[int, float] = {}
    for h in hours_rows:
        enabled_by_room[h.room_id] = enabled_by_room.get(h.room_id, 0.0) + _hours_between(
            h.start_time, h.end_time
        )

    rooms_without_hours: list[IndicadoresRoomRef] = []
    rooms_in_pie = 0
    rooms_without_agenda = 0
    enabled_hours = 0.0
    for room in rooms:
        eh = enabled_by_room.get(room.id, 0.0)
        if eh <= 0:
            rooms_without_hours.append(IndicadoresRoomRef(id=room.id, code=room.code))
            continue
        rooms_in_pie += 1
        enabled_hours += eh
        if not room_agendas.get(room.id):
            rooms_without_agenda += 1

    # Sync blocks for this weekday (Python weekday via dia label).
    occupied_hours = 0.0
    if room_ids:
        rows = list(db.execute(select(OcupacionHorarioActivo)).scalars().all())
        for row in rows:
            fields = agenda_svc._payload_fields(row)
            if agenda_svc._weekday_from_dia(fields["dia"]) != py_weekday:
                continue
            f_desde = agenda_svc._parse_fecha(fields["fecha_desde"])
            f_hasta = agenda_svc._parse_fecha(fields["fecha_hasta"])
            h_desde = agenda_svc._parse_hora(fields["hora_desde"])
            h_hasta = agenda_svc._parse_hora(fields["hora_hasta"])
            if f_desde is None or f_hasta is None or h_desde is None or h_hasta is None:
                continue
            if h_hasta <= h_desde:
                continue
            if not (f_desde <= day <= f_hasta):
                continue
            id_agenda = fields["id_agenda"]
            if id_agenda is None:
                continue
            mapped_room = agenda_rooms.get(id_agenda)
            if mapped_room is None or mapped_room not in room_ids:
                continue
            # Solo aporta a la torta si el room tiene horario ese día.
            if enabled_by_room.get(mapped_room, 0.0) <= 0:
                continue
            if not _match_especialidad(fields["especialidad"], fields["especialidad_agenda"], especialidad):
                continue
            if not _match_medico(fields["medico"], medico):
                continue
            occupied_hours += _hours_between(h_desde, h_hasta)

    free_hours = max(0.0, enabled_hours - occupied_hours)
    percent = round((occupied_hours / enabled_hours) * 100, 2) if enabled_hours > 0 else None

    return IndicadoresOcupacionResponse(
        date=day.isoformat(),
        occupied_hours=round(occupied_hours, 2),
        enabled_hours=round(enabled_hours, 2),
        free_hours=round(free_hours, 2),
        occupancy_percent=percent,
        rooms_included=len(rooms),
        rooms_in_pie=rooms_in_pie,
        rooms_without_hours=rooms_without_hours,
        rooms_without_agenda=rooms_without_agenda,
    )
