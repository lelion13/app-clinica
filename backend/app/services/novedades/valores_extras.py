"""Índices → Valores Extras: cargas del período agrupadas por profesional (control)."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.novedades import MOTIVO_SIN_PRODUCCION_LABELS, MotivoSinProduccion, NovedadesPeriodo
from app.schemas.novedades import (
    GridRowResponse,
    ValoresExtrasDetalleRow,
    ValoresExtrasFiltroLiteral,
    ValoresExtrasProfesionalRow,
    ValoresExtrasResponse,
)
from app.services.novedades.export_xls import build_grid_rows

MODULO_TIPO = "modulo_asignado"


def _require_periodo(db: Session, periodo_id: int) -> NovedadesPeriodo:
    periodo = db.execute(
        select(NovedadesPeriodo).where(
            NovedadesPeriodo.id == periodo_id,
            NovedadesPeriodo.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if not periodo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Periodo no encontrado")
    return periodo


def _motivo_label(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return MOTIVO_SIN_PRODUCCION_LABELS.get(MotivoSinProduccion(value), value)
    except ValueError:
        return value


def row_observation_fields(row: GridRowResponse) -> list[str]:
    """Non-empty observation texts on a carga row (extensible if more fields appear)."""
    out: list[str] = []
    obs = (row.observacion_sin_produccion or "").strip()
    if obs:
        out.append(obs)
    return out


def row_has_observacion(row: GridRowResponse) -> bool:
    return bool(row_observation_fields(row))


def row_matches_filtro(row: GridRowResponse, filtro: ValoresExtrasFiltroLiteral) -> bool:
    is_modulo = row.tipo == MODULO_TIPO
    if filtro == "modulos":
        return is_modulo
    if filtro == "novedades":
        return not is_modulo
    if filtro == "novedad_extra":
        return row_has_observacion(row)
    # ambos
    return True


def professional_matches_q(*, name: str, legajo: str | None, q: str | None) -> bool:
    if not q or not q.strip():
        return True
    needle = q.strip().casefold()
    hay = f"{name or ''} {legajo or ''}".casefold()
    return needle in hay


def _detalle_from_grid(row: GridRowResponse) -> ValoresExtrasDetalleRow:
    is_modulo = row.tipo == MODULO_TIPO
    importe = Decimal(row.valor or 0)
    if is_modulo:
        cantidad = Decimal("1")
        valor_unitario = None
        kind = "modulo"
        tipo_label = "Módulo"
    else:
        cantidad = Decimal(row.horas) if row.horas is not None else None
        valor_unitario = Decimal(row.valor_hora) if row.valor_hora is not None else None
        kind = "novedad"
        tipo_label = "Novedad"
    return ValoresExtrasDetalleRow(
        kind=kind,
        id=row.id,
        fecha_realizacion=row.fecha_realizacion,
        tipo=tipo_label,
        concepto=row.concepto,
        cantidad_horas=cantidad,
        valor_unitario=valor_unitario,
        importe=importe,
        motivo_sin_produccion=row.motivo_sin_produccion,
        motivo_label=_motivo_label(row.motivo_sin_produccion),
        observacion_sin_produccion=(row.observacion_sin_produccion or None),
        observaciones=row_observation_fields(row),
        servicio_nombre=row.servicio_nombre,
    )


def build_valores_extras(
    db: Session,
    *,
    periodo_id: int,
    filtro: ValoresExtrasFiltroLiteral = "ambos",
    q: str | None = None,
    professional_ids: list[int] | None = None,
) -> ValoresExtrasResponse:
    periodo = _require_periodo(db, periodo_id)
    _ = periodo
    detail = build_grid_rows(db, periodo_id=periodo_id, servicio_id=None, q=None, concepto_q=None)
    filtered = [r for r in detail if row_matches_filtro(r, filtro)]

    allow = set(professional_ids) if professional_ids is not None else None

    by_pid: dict[int, list[GridRowResponse]] = defaultdict(list)
    meta: dict[int, tuple[str, str | None]] = {}
    for row in filtered:
        if allow is not None and row.professional_id not in allow:
            continue
        by_pid[row.professional_id].append(row)
        meta[row.professional_id] = (row.professional_name, row.legajo)

    profesionales: list[ValoresExtrasProfesionalRow] = []
    for pid, rows in by_pid.items():
        name, legajo = meta[pid]
        if not professional_matches_q(name=name, legajo=legajo, q=q):
            continue
        cant_modulos = 0
        cant_novedades = 0
        importe_modulos = Decimal("0")
        importe_novedades = Decimal("0")
        detalle: list[ValoresExtrasDetalleRow] = []
        rows_sorted = sorted(
            rows,
            key=lambda r: (r.fecha_realizacion or date.min, r.tipo, r.concepto or ""),
            reverse=True,
        )
        for row in rows_sorted:
            item = _detalle_from_grid(row)
            detalle.append(item)
            if item.kind == "modulo":
                cant_modulos += 1
                importe_modulos += item.importe
            else:
                cant_novedades += 1
                importe_novedades += item.importe
        profesionales.append(
            ValoresExtrasProfesionalRow(
                professional_id=pid,
                legajo=legajo,
                professional_name=name,
                cant_modulos=cant_modulos,
                cant_novedades=cant_novedades,
                importe_modulos=importe_modulos,
                importe_novedades=importe_novedades,
                importe_total=importe_modulos + importe_novedades,
                detalle=detalle,
            )
        )

    # Preserve selection order when ids provided; else name sort
    if professional_ids is not None:
        order = {pid: i for i, pid in enumerate(professional_ids)}
        profesionales.sort(key=lambda r: order.get(r.professional_id, 10_000))
    else:
        profesionales.sort(key=lambda r: (r.professional_name or "").casefold())
    return ValoresExtrasResponse(
        periodo_id=periodo_id,
        filtro=filtro,
        q=q,
        profesionales=profesionales,
    )


def periodo_nombre(db: Session, periodo_id: int) -> str | None:
    periodo = _require_periodo(db, periodo_id)
    return periodo.nombre
