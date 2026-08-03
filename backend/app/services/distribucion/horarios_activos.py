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
    id_raw = raw.get("id")
    id_val: int | None = None
    if isinstance(id_raw, int):
        id_val = id_raw
    elif id_raw is not None:
        try:
            id_val = int(id_raw)
        except (TypeError, ValueError):
            id_val = None

    dominio_raw = raw.get("id_dominio")
    dominio_val: int | None = None
    if isinstance(dominio_raw, int):
        dominio_val = dominio_raw
    elif dominio_raw is not None:
        try:
            dominio_val = int(dominio_raw)
        except (TypeError, ValueError):
            dominio_val = None

    duracion = raw.get("duracion_turno")
    if isinstance(duracion, bool):
        duracion = None
    elif duracion is not None and not isinstance(duracion, (int, float)):
        try:
            duracion = float(duracion)
        except (TypeError, ValueError):
            duracion = None

    tipo, especialidad_agenda, medico = _split_nombre_agenda(raw.get("nombre_agenda"))

    return HorarioActivoItem(
        id_dato=_as_str(raw.get("id_dato")),
        id=id_val,
        id_dominio=dominio_val,
        tipo=tipo,
        especialidad_agenda=especialidad_agenda,
        medico=medico,
        especialidad=_as_str(raw.get("especialidad")),
        fecha_desde=_as_str(raw.get("fecha_desde")),
        hora_desde=_as_str(raw.get("hora_desde")),
        fecha_hasta=_as_str(raw.get("fecha_hasta")),
        hora_hasta=_as_str(raw.get("hora_hasta")),
        duracion_turno=duracion,
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

    rows = _extract_rows(payload)
    return HorariosActivosResponse(items=[_map_row(row) for row in rows])
