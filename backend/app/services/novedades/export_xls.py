from decimal import Decimal
from io import BytesIO

from openpyxl import Workbook
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.novedades import (
    NovedadesAsignacionModulo,
    NovedadesModulo,
    NovedadesNovedad,
    NovedadesPeriodo,
    NovedadesServicio,
)
from app.models.professional import Professional
from app.models.user import User
from app.schemas.novedades import GridRowResponse


def build_grid_rows(
    db: Session,
    *,
    periodo_id: int | None = None,
    servicio_id: int | None = None,
    q: str | None = None,
    modulo_q: str | None = None,
) -> list[GridRowResponse]:
    rows: list[GridRowResponse] = []

    asignaciones = list(
        db.execute(select(NovedadesAsignacionModulo).where(NovedadesAsignacionModulo.deleted_at.is_(None))).scalars().all()
    )
    novedades = list(db.execute(select(NovedadesNovedad).where(NovedadesNovedad.deleted_at.is_(None))).scalars().all())

    for item in asignaciones:
        row = _asignacion_row(db, item)
        if row and _matches(row, periodo_id, servicio_id, q, modulo_q):
            rows.append(row)
    for item in novedades:
        row = _novedad_row(db, item)
        if row and _matches(row, periodo_id, servicio_id, q, modulo_q):
            rows.append(row)

    rows.sort(key=lambda r: r.fecha_carga, reverse=True)
    return rows


def export_xlsx_bytes(
    db: Session,
    *,
    periodo_id: int | None = None,
    servicio_id: int | None = None,
    q: str | None = None,
    modulo_q: str | None = None,
) -> bytes:
    rows = build_grid_rows(db, periodo_id=periodo_id, servicio_id=servicio_id, q=q, modulo_q=modulo_q)
    wb = Workbook()
    ws = wb.active
    ws.title = "Novedades"
    ws.append(
        [
            "periodo",
            "servicio",
            "profesional",
            "tipo",
            "modulo_concepto",
            "valor",
            "justificacion",
            "cargado_por",
            "fecha_carga",
        ]
    )
    for row in rows:
        ws.append(
            [
                row.periodo_nombre or str(row.periodo_id),
                row.servicio_nombre,
                row.professional_name,
                row.tipo,
                row.modulo_descripcion,
                float(row.valor) if row.valor is not None else None,
                row.justificacion,
                row.cargado_por,
                row.fecha_carga.isoformat() if row.fecha_carga else None,
            ]
        )
    buffer = BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def _matches(
    row: GridRowResponse,
    periodo_id: int | None,
    servicio_id: int | None,
    q: str | None,
    modulo_q: str | None,
) -> bool:
    if periodo_id is not None and row.periodo_id != periodo_id:
        return False
    if servicio_id is not None and row.servicio_id != servicio_id:
        return False
    if q:
        needle = q.strip().lower()
        hay = f"{row.professional_name} {row.servicio_nombre}".lower()
        if needle not in hay:
            return False
    if modulo_q:
        needle = modulo_q.strip().lower()
        if needle not in row.modulo_descripcion.lower():
            return False
    return True


def _asignacion_row(db: Session, item: NovedadesAsignacionModulo) -> GridRowResponse | None:
    ctx = _context(db, item.periodo_id, item.servicio_id, item.professional_id, item.modulo_id, item.created_by)
    if not ctx:
        return None
    periodo, servicio, professional, modulo, actor = ctx
    return GridRowResponse(
        tipo="modulo_asignado",
        id=item.id,
        periodo_id=periodo.id,
        periodo_nombre=periodo.nombre,
        servicio_id=servicio.id,
        servicio_nombre=servicio.nombre,
        professional_id=professional.id,
        professional_name=professional.full_name,
        modulo_id=modulo.id,
        modulo_descripcion=modulo.descripcion,
        valor=Decimal(modulo.valor),
        justificacion=None,
        cargado_por=actor.name if actor else None,
        fecha_carga=item.created_at,
    )


def _novedad_row(db: Session, item: NovedadesNovedad) -> GridRowResponse | None:
    ctx = _context(db, item.periodo_id, item.servicio_id, item.professional_id, item.modulo_id, item.created_by)
    if not ctx:
        return None
    periodo, servicio, professional, modulo, actor = ctx
    return GridRowResponse(
        tipo="novedad",
        id=item.id,
        periodo_id=periodo.id,
        periodo_nombre=periodo.nombre,
        servicio_id=servicio.id,
        servicio_nombre=servicio.nombre,
        professional_id=professional.id,
        professional_name=professional.full_name,
        modulo_id=modulo.id,
        modulo_descripcion=modulo.descripcion,
        valor=Decimal(item.valor),
        justificacion=item.justificacion,
        cargado_por=actor.name if actor else None,
        fecha_carga=item.created_at,
    )


def _context(db: Session, periodo_id: int, servicio_id: int, professional_id: int, modulo_id: int, actor_id: int | None):
    periodo = db.execute(select(NovedadesPeriodo).where(NovedadesPeriodo.id == periodo_id)).scalar_one_or_none()
    servicio = db.execute(select(NovedadesServicio).where(NovedadesServicio.id == servicio_id)).scalar_one_or_none()
    professional = db.execute(select(Professional).where(Professional.id == professional_id)).scalar_one_or_none()
    modulo = db.execute(select(NovedadesModulo).where(NovedadesModulo.id == modulo_id)).scalar_one_or_none()
    actor = db.execute(select(User).where(User.id == actor_id)).scalar_one_or_none() if actor_id else None
    if not all([periodo, servicio, professional, modulo]):
        return None
    return periodo, servicio, professional, modulo, actor
