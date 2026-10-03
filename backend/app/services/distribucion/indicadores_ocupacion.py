"""Indicadores de ocupación: horas sync (agendas mapeadas) ÷ horario operativo del box."""

from __future__ import annotations

import calendar
from collections import Counter
from datetime import date, datetime, time

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.calendar import weekday_js_from_date
from app.models.consulting_room import ConsultingRoom, RoomOperatingHour
from app.models.ocupacion import OcupacionHorarioActivo
from app.schemas.distribucion import (
    IndicadoresOcupacionResponse,
    IndicadoresRoomRef,
    IndicadoresTopItem,
)
from app.services import room_agenda_map as room_agenda_map_service
from app.services.distribucion import agenda_ocupacion as agenda_svc

TOP_LIMIT = 10
LABEL_SIN_ESPECIALIDAD = "Sin especialidad"
LABEL_SIN_MEDICO = "Sin médico"


def _hours_between(start: time, end: time) -> float:
    if end <= start:
        return 0.0
    base = date(2000, 1, 1)
    return (datetime.combine(base, end) - datetime.combine(base, start)).total_seconds() / 3600.0


def _parse_date(raw: str | None) -> date:
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


def _parse_month(raw: str | None) -> tuple[int, int]:
    text = (raw or "").strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="month es obligatorio (YYYY-MM)",
        )
    try:
        year_s, month_s = text[:7].split("-", 1)
        year, month = int(year_s), int(month_s)
        if month < 1 or month > 12:
            raise ValueError("month out of range")
        return year, month
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="month con formato inválido (usar YYYY-MM)",
        ) from exc


def _days_in_month(year: int, month: int) -> list[date]:
    last = calendar.monthrange(year, month)[1]
    return [date(year, month, d) for d in range(1, last + 1)]


def _match_especialidad(esp: str | None, selected: str | None) -> bool:
    if not selected:
        return True
    return agenda_svc._match_multi(esp, [selected])


def _match_medico(medico_payload: str | None, selected: str | None) -> bool:
    if not selected:
        return True
    return agenda_svc._match_medico_payload(medico_payload, [selected])


def _build_tops(
    hours_by_label: dict[str, float],
    *,
    enabled_hours: float,
    occupied_hours: float,
) -> list[IndicadoresTopItem]:
    items = sorted(hours_by_label.items(), key=lambda kv: (-kv[1], kv[0].casefold()))
    out: list[IndicadoresTopItem] = []
    for label, hours in items[:TOP_LIMIT]:
        if hours <= 0:
            continue
        percent_box = round((hours / enabled_hours) * 100, 2) if enabled_hours > 0 else None
        percent_occupied = round((hours / occupied_hours) * 100, 2) if occupied_hours > 0 else None
        out.append(
            IndicadoresTopItem(
                label=label,
                hours=round(hours, 2),
                percent_box=percent_box,
                percent_occupied=percent_occupied,
            )
        )
    return out


def compute_indicadores(
    db: Session,
    *,
    period: str = "day",
    date_str: str | None = None,
    month_str: str | None = None,
    location_id: int | None = None,
    room_id: int | None = None,
    especialidad: str | None = None,
    medico: str | None = None,
) -> IndicadoresOcupacionResponse:
    period_norm = (period or "day").strip().lower()
    if period_norm not in ("day", "month"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="period debe ser day o month",
        )

    if period_norm == "day":
        day = _parse_date(date_str)
        days = [day]
        date_out: str | None = day.isoformat()
        month_out: str | None = None
    else:
        year, month = _parse_month(month_str)
        days = _days_in_month(year, month)
        date_out = None
        month_out = f"{year:04d}-{month:02d}"

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

    hours_rows: list[RoomOperatingHour] = []
    if room_ids:
        hours_rows = list(
            db.execute(
                select(RoomOperatingHour).where(
                    RoomOperatingHour.deleted_at.is_(None),
                    RoomOperatingHour.room_id.in_(room_ids),
                )
            )
            .scalars()
            .all()
        )

    hours_by_room_wd: dict[tuple[int, int], float] = {}
    for h in hours_rows:
        key = (h.room_id, int(h.weekday))
        hours_by_room_wd[key] = hours_by_room_wd.get(key, 0.0) + _hours_between(h.start_time, h.end_time)

    wd_counts = Counter(weekday_js_from_date(d) for d in days)
    enabled_by_room: dict[int, float] = {r.id: 0.0 for r in rooms}
    for room in rooms:
        total = 0.0
        for js_wd, count in wd_counts.items():
            total += hours_by_room_wd.get((room.id, js_wd), 0.0) * count
        enabled_by_room[room.id] = total

    rooms_without_hours: list[IndicadoresRoomRef] = []
    rooms_in_pie = 0
    rooms_without_agenda = 0
    enabled_hours = 0.0
    pie_room_ids: set[int] = set()
    for room in rooms:
        eh = enabled_by_room.get(room.id, 0.0)
        if eh <= 0:
            rooms_without_hours.append(IndicadoresRoomRef(id=room.id, code=room.code))
            continue
        rooms_in_pie += 1
        pie_room_ids.add(room.id)
        enabled_hours += eh
        if not room_agendas.get(room.id):
            rooms_without_agenda += 1

    occupied_hours = 0.0
    top_esp: dict[str, float] = {}
    top_med: dict[str, float] = {}

    if room_ids and pie_room_ids:
        rows = list(db.execute(select(OcupacionHorarioActivo)).scalars().all())
        days_by_py_weekday: dict[int, list[date]] = {}
        for d in days:
            days_by_py_weekday.setdefault(d.weekday(), []).append(d)

        for row in rows:
            fields = agenda_svc._payload_fields(row)
            py_weekday = agenda_svc._weekday_from_dia(fields["dia"])
            if py_weekday is None:
                continue
            candidate_days = days_by_py_weekday.get(py_weekday) or []
            if not candidate_days:
                continue

            f_desde = agenda_svc._parse_fecha(fields["fecha_desde"])
            f_hasta = agenda_svc._parse_fecha(fields["fecha_hasta"])
            h_desde = agenda_svc._parse_hora(fields["hora_desde"])
            h_hasta = agenda_svc._parse_hora(fields["hora_hasta"])
            if f_desde is None or f_hasta is None or h_desde is None or h_hasta is None:
                continue
            if h_hasta <= h_desde:
                continue

            id_agenda = fields["id_agenda"]
            if id_agenda is None:
                continue
            mapped_room = agenda_rooms.get(id_agenda)
            if mapped_room is None or mapped_room not in pie_room_ids:
                continue
            if not _match_especialidad(fields["especialidad"], especialidad):
                continue
            if not _match_medico(fields["medico_payload"], medico):
                continue

            block_hours = _hours_between(h_desde, h_hasta)
            if block_hours <= 0:
                continue

            occurrences = sum(1 for d in candidate_days if f_desde <= d <= f_hasta)
            if occurrences <= 0:
                continue

            add = block_hours * occurrences
            occupied_hours += add

            esp_label = (fields["especialidad"] or "").strip() or LABEL_SIN_ESPECIALIDAD
            med_label = (fields["medico_payload"] or "").strip() or LABEL_SIN_MEDICO
            top_esp[esp_label] = top_esp.get(esp_label, 0.0) + add
            top_med[med_label] = top_med.get(med_label, 0.0) + add

    free_hours = max(0.0, enabled_hours - occupied_hours)
    percent = round((occupied_hours / enabled_hours) * 100, 2) if enabled_hours > 0 else None

    return IndicadoresOcupacionResponse(
        period=period_norm,
        date=date_out,
        month=month_out,
        occupied_hours=round(occupied_hours, 2),
        enabled_hours=round(enabled_hours, 2),
        free_hours=round(free_hours, 2),
        occupancy_percent=percent,
        rooms_included=len(rooms),
        rooms_in_pie=rooms_in_pie,
        rooms_without_hours=rooms_without_hours,
        rooms_without_agenda=rooms_without_agenda,
        top_especialidad=_build_tops(top_esp, enabled_hours=enabled_hours, occupied_hours=occupied_hours),
        top_medico=_build_tops(top_med, enabled_hours=enabled_hours, occupied_hours=occupied_hours),
    )
