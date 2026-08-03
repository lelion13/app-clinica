from datetime import date, datetime
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
    id_dato = _as_str(raw.get("id_dato"))
    if not id_dato:
        return None
    tipo, especialidad_agenda, medico = _split_nombre_agenda(raw.get("nombre_agenda"))
    return OcupacionHorarioActivo(
        id_dato=id_dato[:80],
        horario_id=_as_int(raw.get("id")),
        id_agenda=_as_int(raw.get("id_agenda")),
        id_dominio=_as_int(raw.get("id_dominio")),
        area_jerarquica_id=_as_int(raw.get("area_jerarquica_id")),
        nombre_agenda=_as_str(raw.get("nombre_agenda")),
        tipo=tipo,
        especialidad_agenda=especialidad_agenda,
        medico=medico,
        especialidad=_as_str(raw.get("especialidad")),
        tipo_agenda=_as_str(raw.get("tipo_agenda")),
        consultorio=_as_str(raw.get("consultorio")),
        dia=_as_str(raw.get("dia")),
        dia_de_agenda=_as_str(raw.get("dia_de_agenda")),
        fecha_desde=_as_str(raw.get("fecha_desde")),
        hora_desde=_as_str(raw.get("hora_desde")),
        fecha_hasta=_as_str(raw.get("fecha_hasta")),
        hora_hasta=_as_str(raw.get("hora_hasta")),
        periodo_desde=_as_str(raw.get("periodo_desde")),
        periodo_hasta=_as_str(raw.get("periodo_hasta")),
        duracion_turno=_as_number(raw.get("duracion_turno")),
        cantidad_turnos=_as_number(raw.get("cantidad_turnos")),
        cantidad_sobreturno=_as_number(raw.get("cantidad_sobreturno")),
        horas_funcionamiento=_as_number(raw.get("horas_funcionamiento")),
        capacidad_turnos_15_min=_as_number(raw.get("capacidad_turnos_15_min")),
        tiempo_consultorio=_as_number(raw.get("tiempo_consultorio")),
        estado_agenda=_as_str(raw.get("estado_agenda")),
        estado_horario=_as_str(raw.get("estado_horario")),
        atiende_feriado=_as_str(raw.get("atiende_feriado")),
        dias_limite_visualizacion_pantalla=_as_int(raw.get("dias_limite_visualizacion_pantalla")),
        dias_solicitud_turnos=_as_int(raw.get("dias_solicitud_turnos")),
        medico_responsable=_as_str(raw.get("medico_responsable")),
        medico_responsable_equipo=_as_str(raw.get("medico_responsable_equipo")),
        fecha_ultima_modificacion_agenda=_as_str(raw.get("fecha_ultima_modificacion_agenda")),
        fecha_creacion_horario=_as_str(raw.get("fecha_creacion_horario")),
        synced_at=synced_at,
    )


def _model_to_item(row: OcupacionHorarioActivo) -> HorarioActivoItem:
    return HorarioActivoItem(
        id_dato=row.id_dato,
        id=row.horario_id,
        id_agenda=row.id_agenda,
        id_dominio=row.id_dominio,
        tipo=row.tipo,
        especialidad_agenda=row.especialidad_agenda,
        medico=row.medico,
        especialidad=row.especialidad,
        dia=row.dia,
        fecha_desde=row.fecha_desde,
        hora_desde=row.hora_desde,
        fecha_hasta=row.fecha_hasta,
        hora_hasta=row.hora_hasta,
        duracion_turno=row.duracion_turno,
        cantidad_turnos=row.cantidad_turnos,
        cantidad_sobreturno=row.cantidad_sobreturno,
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
    synced_at = datetime.utcnow()
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


# Compat tests / helpers
def _map_row(raw: dict) -> HorarioActivoItem:
    model = _raw_to_model(raw, synced_at=datetime.utcnow())
    if model is None:
        return HorarioActivoItem()
    return _model_to_item(model)
