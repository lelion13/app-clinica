import copy
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

import httpx
from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.ocupacion import OcupacionHorarioActivo
from app.schemas.distribucion import HorarioActivoItem, HorariosActivosResponse, HorariosActivosSyncResponse


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


def _fetch_remote_rows() -> list[dict]:
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
    return _extract_rows(payload)


def _raw_to_model(raw: dict, synced_at: datetime) -> OcupacionHorarioActivo | None:
    """Persiste el objeto del endpoint tal cual en `payload` (copia profunda)."""
    id_dato = _as_str(raw.get("id_dato"))
    if not id_dato:
        return None
    # Copia exacta de claves/valores del endpoint (sin renombrar ni tipar).
    payload = copy.deepcopy(raw)
    tipo, especialidad_agenda, medico = _split_nombre_agenda(payload.get("nombre_agenda"))
    fecha_hasta = payload.get("fecha_hasta")
    fecha_hasta_str = None if fecha_hasta is None else str(fecha_hasta)
    return OcupacionHorarioActivo(
        id_dato=id_dato[:120],
        payload=payload,
        tipo=tipo,
        especialidad_agenda=especialidad_agenda,
        medico=medico,
        fecha_hasta=fecha_hasta_str,
        synced_at=synced_at,
    )


def _model_to_item(row: OcupacionHorarioActivo) -> HorarioActivoItem:
    """UI lee valores del payload original; derivados desde columnas tipadas."""
    raw = row.payload if isinstance(row.payload, dict) else {}
    return HorarioActivoItem(
        id_dato=_as_str(raw.get("id_dato")) or row.id_dato,
        id=_as_int(raw.get("id")),
        id_agenda=_as_int(raw.get("id_agenda")),
        id_dominio=_as_int(raw.get("id_dominio")),
        tipo=row.tipo,
        especialidad_agenda=row.especialidad_agenda,
        medico=row.medico,
        # especialidad tal cual en payload (sin strip extra al persistir; strip solo en lectura UI)
        especialidad=_as_str(raw.get("especialidad")),
        dia=_as_str(raw.get("dia")),
        fecha_desde=_as_str(raw.get("fecha_desde")),
        hora_desde=_as_str(raw.get("hora_desde")),
        fecha_hasta=_as_str(raw.get("fecha_hasta")) or row.fecha_hasta,
        hora_hasta=_as_str(raw.get("hora_hasta")),
        duracion_turno=_as_number(raw.get("duracion_turno")),
        cantidad_turnos=_as_number(raw.get("cantidad_turnos")),
        cantidad_sobreturno=_as_number(raw.get("cantidad_sobreturno")),
    )


def list_horarios_activos(db: Session) -> HorariosActivosResponse:
    """Lee snapshot local; filtra vigencia fecha_hasta >= hoy (Q27=A)."""
    today = _business_today()
    rows = db.execute(select(OcupacionHorarioActivo)).scalars().all()
    items = [_model_to_item(row) for row in rows if _fecha_hasta_vigente(row.fecha_hasta, today=today)]
    return HorariosActivosResponse(items=items)


def sync_horarios_activos(db: Session) -> HorariosActivosSyncResponse:
    """GET externo OK → wipe + reload en una transacción (Q24=A)."""
    remote_rows = _fetch_remote_rows()
    synced_at = datetime.now(timezone.utc)
    by_id_dato: dict[str, OcupacionHorarioActivo] = {}
    skipped = 0
    for raw in remote_rows:
        model = _raw_to_model(raw, synced_at=synced_at)
        if model is None:
            skipped += 1
            continue
        by_id_dato[model.id_dato] = model

    try:
        db.execute(delete(OcupacionHorarioActivo))
        if by_id_dato:
            db.add_all(list(by_id_dato.values()))
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al persistir horarios activos",
        ) from exc

    return HorariosActivosSyncResponse(synced=len(by_id_dato), skipped=skipped)


def _map_row(raw: dict) -> HorarioActivoItem:
    model = _raw_to_model(raw, synced_at=datetime.now(timezone.utc))
    if model is None:
        return HorarioActivoItem()
    return _model_to_item(model)
