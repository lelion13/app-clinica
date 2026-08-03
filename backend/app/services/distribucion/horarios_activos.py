from datetime import date, datetime
from zoneinfo import ZoneInfo

import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.distribucion import HorarioActivoItem, HorariosActivosResponse


NOMBRE_AGENDA_SEP = " - "


def _as_str(value) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    return s or None


def _as_int(value) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _as_number(value) -> int | float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _business_today() -> date:
    return datetime.now(ZoneInfo(settings.business_tz)).date()


def _parse_fecha(value: str | None) -> date | None:
    text = _as_str(value)
    if not text:
        return None
    # Soporta "YYYY-MM-DD", "YYYY-MM-DD HH:MM:SS", ISO con T.
    date_part = text[:10]
    try:
        return date.fromisoformat(date_part)
    except ValueError:
        return None


def _fecha_hasta_vigente(fecha_hasta: str | None, today: date | None = None) -> bool:
    parsed = _parse_fecha(fecha_hasta)
    if parsed is None:
        return False
    ref = today if today is not None else _business_today()
    return parsed >= ref


def _split_nombre_agenda(nombre: str | None) -> tuple[str | None, str | None, str | None]:
    """Parte nombre_agenda por ' - ': tipo, especialidad_agenda, resto → medico."""
    text = _as_str(nombre)
    if not text:
        return None, None, None
    parts = [p.strip() for p in text.split(NOMBRE_AGENDA_SEP)]
    parts = [p for p in parts if p]
    if not parts:
        return None, None, None
    tipo = parts[0] if len(parts) >= 1 else None
    especialidad_agenda = parts[1] if len(parts) >= 2 else None
    medico = NOMBRE_AGENDA_SEP.join(parts[2:]) if len(parts) >= 3 else None
    return tipo, especialidad_agenda, medico


def _map_row(raw: dict) -> HorarioActivoItem:
    tipo, especialidad_agenda, medico = _split_nombre_agenda(raw.get("nombre_agenda"))

    return HorarioActivoItem(
        id_dato=_as_str(raw.get("id_dato")),
        id=_as_int(raw.get("id")),
        id_agenda=_as_int(raw.get("id_agenda")),
        id_dominio=_as_int(raw.get("id_dominio")),
        tipo=tipo,
        especialidad_agenda=especialidad_agenda,
        medico=medico,
        especialidad=_as_str(raw.get("especialidad")),
        dia=_as_str(raw.get("dia")),
        fecha_desde=_as_str(raw.get("fecha_desde")),
        hora_desde=_as_str(raw.get("hora_desde")),
        fecha_hasta=_as_str(raw.get("fecha_hasta")),
        hora_hasta=_as_str(raw.get("hora_hasta")),
        duracion_turno=_as_number(raw.get("duracion_turno")),
        cantidad_turnos=_as_number(raw.get("cantidad_turnos")),
        cantidad_sobreturno=_as_number(raw.get("cantidad_sobreturno")),
    )


def _extract_rows(payload: object) -> list[dict]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        for key in ("items", "data", "horarios", "results"):
            inner = payload.get(key)
            if isinstance(inner, list):
                return [row for row in inner if isinstance(row, dict)]
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="Respuesta externa de horarios activos con formato no reconocido",
    )


def fetch_horarios_activos() -> HorariosActivosResponse:
    url = (settings.distribucion_horarios_activos_url or "").strip()
    token = (settings.novedades_prof_sync_token or "").strip()
    if not url or not token:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Ocupación no configurada (DISTRIBUCION_HORARIOS_ACTIVOS_URL / NOVEDADES_PROF_SYNC_TOKEN)",
        )
    try:
        with httpx.Client(timeout=settings.distribucion_horarios_activos_timeout) as client:
            response = client.get(
                url,
                headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            )
            response.raise_for_status()
            payload = response.json()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Error al consultar API externa de horarios activos",
        ) from exc

    today = _business_today()
    items = [_map_row(row) for row in _extract_rows(payload)]
    vigentes = [item for item in items if _fecha_hasta_vigente(item.fecha_hasta, today=today)]
    return HorariosActivosResponse(items=vigentes)
