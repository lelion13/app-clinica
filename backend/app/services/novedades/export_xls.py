from collections import defaultdict
from datetime import date
from decimal import Decimal
from io import BytesIO

from openpyxl import Workbook
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.novedades import (
    NOVEDAD_TIPO_LABELS,
    NovedadesAsignacionModulo,
    NovedadesModulo,
    NovedadesNovedad,
    NovedadesPeriodo,
    NovedadesProfesional,
    NovedadesServicio,
    NovedadTipo,
)
from app.models.user import User
from app.schemas.novedades import GridRowResponse
from app.services.novedades.helpers import novedad_valor_calculado

_DETAIL_HEADERS = [
    "periodo",
    "servicio",
    "profesional",
    "tipo",
    "concepto",
    "horas",
    "valor_hora",
    "valor",
    "cargado_por",
    "fecha_realizacion",
    "fecha_carga",
]


def build_grid_rows(
    db: Session,
    *,
    periodo_id: int | None = None,
    servicio_id: int | None = None,
    professional_id: int | None = None,
    q: str | None = None,
    concepto_q: str | None = None,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
) -> list[GridRowResponse]:
    rows: list[GridRowResponse] = []

    asignaciones = list(
        db.execute(select(NovedadesAsignacionModulo).where(NovedadesAsignacionModulo.deleted_at.is_(None))).scalars().all()
    )
    novedades = list(db.execute(select(NovedadesNovedad).where(NovedadesNovedad.deleted_at.is_(None))).scalars().all())

    for item in asignaciones:
        row = _asignacion_row(db, item)
        if row and _matches(
            row, periodo_id, servicio_id, professional_id, q, concepto_q, fecha_desde, fecha_hasta
        ):
            rows.append(row)
    for item in novedades:
        row = _novedad_row(db, item)
        if row and _matches(
            row, periodo_id, servicio_id, professional_id, q, concepto_q, fecha_desde, fecha_hasta
        ):
            rows.append(row)

    rows.sort(key=lambda r: r.fecha_carga, reverse=True)
    return rows


def export_xlsx_bytes(
    db: Session,
    *,
    periodo_id: int | None = None,
    servicio_id: int | None = None,
    q: str | None = None,
    concepto_q: str | None = None,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
) -> bytes:
    rows = build_grid_rows(
        db,
        periodo_id=periodo_id,
        servicio_id=servicio_id,
        q=q,
        concepto_q=concepto_q,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )
    wb = Workbook()
    if fecha_desde is not None and fecha_hasta is not None:
        ws_resumen = wb.active
        ws_resumen.title = "Resumen"
        ws_resumen.append(["legajo", "nombre", "total_cargas"])
        for summary in _resumen_rows(rows):
            ws_resumen.append(summary)

        ws_detalle = wb.create_sheet("Detalle")
        _append_detail_sheet(ws_detalle, rows)
    else:
        ws = wb.active
        ws.title = "Novedades"
        _append_detail_sheet(ws, rows)

    buffer = BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def _append_detail_sheet(ws, rows: list[GridRowResponse]) -> None:
    ws.append(list(_DETAIL_HEADERS))
    for row in rows:
        ws.append(
            [
                row.periodo_nombre or str(row.periodo_id),
                row.servicio_nombre,
                row.professional_name,
                row.tipo,
                row.concepto,
                float(row.horas) if row.horas is not None else None,
                float(row.valor_hora) if row.valor_hora is not None else None,
                float(row.valor) if row.valor is not None else None,
                row.cargado_por,
                row.fecha_realizacion.isoformat() if row.fecha_realizacion else None,
                row.fecha_carga.isoformat() if row.fecha_carga else None,
            ]
        )


def _resumen_rows(rows: list[GridRowResponse]) -> list[list]:
    by_prof: dict[int, dict] = {}
    totals: dict[int, Decimal] = defaultdict(lambda: Decimal("0"))
    for row in rows:
        if row.professional_id not in by_prof:
            by_prof[row.professional_id] = {
                "legajo": row.legajo,
                "nombre": row.professional_name,
            }
        if row.valor is not None:
            totals[row.professional_id] += Decimal(row.valor)

    out: list[list] = []
    for pid in sorted(by_prof.keys(), key=lambda i: (by_prof[i]["nombre"] or "").lower()):
        info = by_prof[pid]
        out.append([info["legajo"], info["nombre"], float(totals[pid])])
    return out


def _matches(
    row: GridRowResponse,
    periodo_id: int | None,
    servicio_id: int | None,
    professional_id: int | None,
    q: str | None,
    concepto_q: str | None,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
) -> bool:
    if periodo_id is not None and row.periodo_id != periodo_id:
        return False
    if servicio_id is not None and row.servicio_id != servicio_id:
        return False
    if professional_id is not None and row.professional_id != professional_id:
        return False
    if fecha_desde is not None or fecha_hasta is not None:
        if row.fecha_realizacion is None:
            return False
        if fecha_desde is not None and row.fecha_realizacion < fecha_desde:
            return False
        if fecha_hasta is not None and row.fecha_realizacion > fecha_hasta:
            return False
    if q:
        needle = q.strip().lower()
        hay = f"{row.professional_name} {row.servicio_nombre}".lower()
        if needle not in hay:
            return False
    if concepto_q:
        needle = concepto_q.strip().lower()
        if needle not in row.concepto.lower() and needle not in row.tipo.lower():
            return False
    return True


def _asignacion_row(db: Session, item: NovedadesAsignacionModulo) -> GridRowResponse | None:
    periodo, servicio, professional, actor = _base_context(
        db, item.periodo_id, item.servicio_id, item.professional_id, item.created_by
    )
    if not all([periodo, servicio, professional]):
        return None
    modulo = db.execute(select(NovedadesModulo).where(NovedadesModulo.id == item.modulo_id)).scalar_one_or_none()
    if not modulo:
        return None
    valor = Decimal(item.valor) if getattr(item, "valor", None) is not None else Decimal(modulo.valor)
    return GridRowResponse(
        tipo="modulo_asignado",
        id=item.id,
        periodo_id=periodo.id,
        periodo_nombre=periodo.nombre,
        servicio_id=servicio.id,
        servicio_nombre=servicio.nombre,
        professional_id=professional.id,
        professional_name=professional.full_name,
        legajo=professional.legajo,
        concepto=modulo.descripcion,
        horas=None,
        valor=valor,
        valor_hora=None,
        cargado_por=actor.name if actor else None,
        fecha_realizacion=item.fecha_realizacion,
        fecha_carga=item.created_at,
    )


def _novedad_row(db: Session, item: NovedadesNovedad) -> GridRowResponse | None:
    periodo, servicio, professional, actor = _base_context(
        db, item.periodo_id, item.servicio_id, item.professional_id, item.created_by
    )
    if not all([periodo, servicio, professional]):
        return None
    tipo = item.tipo if isinstance(item.tipo, NovedadTipo) else NovedadTipo(item.tipo)
    label = NOVEDAD_TIPO_LABELS.get(tipo, str(item.tipo))
    horas = Decimal(item.horas)
    valor_hora = Decimal(servicio.valor_hora or 0)
    return GridRowResponse(
        tipo=tipo.value,
        id=item.id,
        periodo_id=periodo.id,
        periodo_nombre=periodo.nombre,
        servicio_id=servicio.id,
        servicio_nombre=servicio.nombre,
        professional_id=professional.id,
        professional_name=professional.full_name,
        legajo=professional.legajo,
        concepto=label,
        horas=horas,
        valor=novedad_valor_calculado(tipo, horas, valor_hora),
        valor_hora=valor_hora,
        cargado_por=actor.name if actor else None,
        fecha_realizacion=item.fecha_realizacion,
        fecha_carga=item.created_at,
    )


def _base_context(db: Session, periodo_id: int, servicio_id: int, professional_id: int, actor_id: int | None):
    periodo = db.execute(select(NovedadesPeriodo).where(NovedadesPeriodo.id == periodo_id)).scalar_one_or_none()
    servicio = db.execute(select(NovedadesServicio).where(NovedadesServicio.id == servicio_id)).scalar_one_or_none()
    professional = db.execute(
        select(NovedadesProfesional).where(NovedadesProfesional.id == professional_id)
    ).scalar_one_or_none()
    actor = db.execute(select(User).where(User.id == actor_id)).scalar_one_or_none() if actor_id else None
    return periodo, servicio, professional, actor
