"""Materializa eventos de calendario desde ocupacion_horario_activo (ventana + filtros)."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.location import Location
from app.models.ocupacion import OcupacionHorarioActivo
from app.schemas.distribucion import (
    AgendaFilterOption,
    AgendaFilterOptionsResponse,
    AgendaOcupacionEvent,
    AgendaOcupacionEventExtended,
    AgendaOcupacionEventsResponse,
)


DIA_TO_WEEKDAY = {
    "lunes": 0,
    "martes": 1,
    "miercoles": 2,
    "miércoles": 2,
    "jueves": 3,
    "viernes": 4,
    "sabado": 5,
    "sábado": 5,
    "domingo": 6,
}


def _tz() -> ZoneInfo:
    return ZoneInfo(settings.business_tz)


def _as_str(value) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    return s or None


def _norm(value: str | None) -> str:
    return (value or "").strip().casefold()


def _parse_fecha(value: str | None) -> date | None:
    text = _as_str(value)
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def _parse_bound(raw: str, *, is_end: bool) -> date:
    text = (raw or "").strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start y end son obligatorios",
        )
    try:
        if "T" in text or " " in text:
            dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
            if dt.tzinfo is not None:
                dt = dt.astimezone(_tz())
            d = dt.date()
            # FullCalendar end is exclusive; if time > midnight keep date as-is
            if is_end and (dt.hour or dt.minute or dt.second):
                return d
            return d
        return date.fromisoformat(text[:10])
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start/end con formato inválido (usar YYYY-MM-DD)",
        ) from exc


def _parse_hora(value: str | None) -> time | None:
    text = _as_str(value)
    if not text:
        return None
    parts = text.replace(".", ":").split(":")
    try:
        h = int(parts[0])
        m = int(parts[1]) if len(parts) > 1 else 0
        s = int(parts[2]) if len(parts) > 2 else 0
        return time(hour=h, minute=m, second=s)
    except (TypeError, ValueError, IndexError):
        return None


def _weekday_from_dia(dia: str | None) -> int | None:
    key = _norm(dia)
    if not key:
        return None
    return DIA_TO_WEEKDAY.get(key)


def _ranges_overlap(a_start: date, a_end: date, b_start: date, b_end_exclusive: date) -> bool:
    """Fila [a_start, a_end] inclusive vs ventana [b_start, b_end_exclusive)."""
    return a_start < b_end_exclusive and a_end >= b_start


def _location_labels(db: Session) -> dict[int, str]:
    rows = db.execute(select(Location).where(Location.deleted_at.is_(None))).scalars().all()
    out: dict[int, str] = {}
    for loc in rows:
        if loc.id_dominio is None:
            continue
        name = _as_str(loc.name)
        if name:
            out[int(loc.id_dominio)] = name
    return out


def _dominio_label(id_dominio: int | None, labels: dict[int, str]) -> str | None:
    if id_dominio is None:
        return None
    return labels.get(int(id_dominio)) or str(id_dominio)


def _payload_fields(row: OcupacionHorarioActivo) -> dict:
    raw = row.payload if isinstance(row.payload, dict) else {}
    id_dominio = raw.get("id_dominio")
    try:
        id_dominio_int = int(id_dominio) if id_dominio is not None and id_dominio != "" else None
    except (TypeError, ValueError):
        id_dominio_int = None
    return {
        "id_dato": _as_str(raw.get("id_dato")) or row.id_dato,
        "id_dominio": id_dominio_int,
        "tipo": row.tipo or _as_str(raw.get("tipo")),
        "especialidad_agenda": row.especialidad_agenda,
        "medico": row.medico or _as_str(raw.get("medico")),
        "especialidad": _as_str(raw.get("especialidad")),
        "dia": _as_str(raw.get("dia")),
        "fecha_desde": _as_str(raw.get("fecha_desde")) or None,
        "hora_desde": _as_str(raw.get("hora_desde")),
        "fecha_hasta": _as_str(raw.get("fecha_hasta")) or row.fecha_hasta,
        "hora_hasta": _as_str(raw.get("hora_hasta")),
        "duracion_turno": raw.get("duracion_turno"),
        "cantidad_turnos": raw.get("cantidad_turnos"),
        "cantidad_sobreturno": raw.get("cantidad_sobreturno"),
    }


def _match_multi(value: str | None, selected: list[str]) -> bool:
    if not selected:
        return True
    needle = _norm(value)
    if not needle:
        return False
    return any(_norm(item) == needle for item in selected)


def _match_especialidad(esp: str | None, esp_agenda: str | None, selected: list[str]) -> bool:
    if not selected:
        return True
    return _match_multi(esp, selected) or _match_multi(esp_agenda, selected)


def _match_id_dominio(id_dominio: int | None, selected: list[str]) -> bool:
    if not selected:
        return True
    if id_dominio is None:
        return False
    token = str(id_dominio)
    return any(str(item).strip() == token for item in selected)


def list_filter_options(db: Session) -> AgendaFilterOptionsResponse:
    labels = _location_labels(db)
    rows = db.execute(select(OcupacionHorarioActivo)).scalars().all()

    dominios: dict[str, str] = {}
    tipos: set[str] = set()
    especialidades: set[str] = set()
    medicos: set[str] = set()
    dias: set[str] = set()

    for row in rows:
        fields = _payload_fields(row)
        if fields["id_dominio"] is not None:
            key = str(fields["id_dominio"])
            dominios[key] = _dominio_label(fields["id_dominio"], labels) or key
        if fields["tipo"]:
            tipos.add(fields["tipo"])
        if fields["especialidad"]:
            especialidades.add(fields["especialidad"])
        if fields["especialidad_agenda"]:
            especialidades.add(fields["especialidad_agenda"])
        if fields["medico"]:
            medicos.add(fields["medico"])
        if fields["dia"] and _weekday_from_dia(fields["dia"]) is not None:
            dias.add(fields["dia"].strip().lower())

    return AgendaFilterOptionsResponse(
        id_dominio=[
            AgendaFilterOption(value=k, label=dominios[k])
            for k in sorted(dominios.keys(), key=lambda x: int(x) if x.isdigit() else x)
        ],
        tipo=[AgendaFilterOption(value=v, label=v) for v in sorted(tipos, key=str.casefold)],
        especialidad=[
            AgendaFilterOption(value=v, label=v) for v in sorted(especialidades, key=str.casefold)
        ],
        medico=[AgendaFilterOption(value=v, label=v) for v in sorted(medicos, key=str.casefold)],
        dia=[AgendaFilterOption(value=v, label=v) for v in sorted(dias, key=str.casefold)],
    )


def list_agenda_events(
    db: Session,
    *,
    start: str,
    end: str,
    id_dominio: list[str] | None = None,
    tipo: list[str] | None = None,
    especialidad: list[str] | None = None,
    medico: list[str] | None = None,
    dia: list[str] | None = None,
) -> AgendaOcupacionEventsResponse:
    win_start = _parse_bound(start, is_end=False)
    win_end = _parse_bound(end, is_end=True)
    if win_end <= win_start:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="end debe ser posterior a start",
        )

    f_dom = id_dominio or []
    f_tipo = tipo or []
    f_esp = especialidad or []
    f_med = medico or []
    f_dia = dia or []

    labels = _location_labels(db)
    rows = db.execute(select(OcupacionHorarioActivo)).scalars().all()
    events: list[AgendaOcupacionEvent] = []

    for row in rows:
        fields = _payload_fields(row)
        weekday = _weekday_from_dia(fields["dia"])
        if weekday is None:
            continue

        f_desde = _parse_fecha(fields["fecha_desde"])
        f_hasta = _parse_fecha(fields["fecha_hasta"])
        h_desde = _parse_hora(fields["hora_desde"])
        h_hasta = _parse_hora(fields["hora_hasta"])
        if f_desde is None or f_hasta is None or h_desde is None or h_hasta is None:
            continue
        if h_hasta <= h_desde:
            continue
        if not _ranges_overlap(f_desde, f_hasta, win_start, win_end):
            continue

        if not _match_id_dominio(fields["id_dominio"], f_dom):
            continue
        if not _match_multi(fields["tipo"], f_tipo):
            continue
        if not _match_especialidad(fields["especialidad"], fields["especialidad_agenda"], f_esp):
            continue
        if not _match_multi(fields["medico"], f_med):
            continue
        if not _match_multi(fields["dia"], f_dia):
            continue

        loc_name = _dominio_label(fields["id_dominio"], labels)
        extended = AgendaOcupacionEventExtended(
            row_id=row.id,
            id_dato=fields["id_dato"],
            id_dominio=fields["id_dominio"],
            location_name=loc_name,
            tipo=fields["tipo"],
            especialidad_agenda=fields["especialidad_agenda"],
            medico=fields["medico"],
            especialidad=fields["especialidad"],
            dia=fields["dia"],
            fecha_desde=fields["fecha_desde"],
            hora_desde=fields["hora_desde"],
            fecha_hasta=fields["fecha_hasta"],
            hora_hasta=fields["hora_hasta"],
            duracion_turno=fields["duracion_turno"]
            if isinstance(fields["duracion_turno"], (int, float))
            else None,
            cantidad_turnos=fields["cantidad_turnos"]
            if isinstance(fields["cantidad_turnos"], (int, float))
            else None,
            cantidad_sobreturno=fields["cantidad_sobreturno"]
            if isinstance(fields["cantidad_sobreturno"], (int, float))
            else None,
        )

        day = win_start
        while day < win_end:
            if (
                day.weekday() == weekday
                and f_desde <= day <= f_hasta
            ):
                start_dt = datetime.combine(day, h_desde)
                end_dt = datetime.combine(day, h_hasta)
                events.append(
                    AgendaOcupacionEvent(
                        id=f"{row.id}:{day.isoformat()}",
                        title=fields["medico"] or "",
                        start=start_dt.isoformat(timespec="seconds"),
                        end=end_dt.isoformat(timespec="seconds"),
                        extended=extended,
                    )
                )
            day += timedelta(days=1)

    events.sort(key=lambda e: (e.start, e.title or "", e.id))
    return AgendaOcupacionEventsResponse(events=events)
