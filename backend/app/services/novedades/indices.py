"""Índices (admin): agregados por servicio y por profesional para un período."""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.novedades import NovedadesAjusteCapital, NovedadesPeriodo, NovedadesProfesional, NovedadesServicio
from app.schemas.novedades import (
    IndicesProfesionalRow,
    IndicesResponse,
    IndicesServicioRow,
)
from app.services.novedades.capital_humano import build_capital_humano_rows
from app.services.novedades.export_xls import build_grid_rows

DESCONTAR_TIPOS = frozenset({"horas_a_descontar"})


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


def signed_horas(tipo: str | None, horas: Decimal | None) -> Decimal:
    """Net hours contribution for a novedad row (modules contribute 0)."""
    if horas is None:
        return Decimal("0")
    qty = Decimal(horas)
    tipo_key = (tipo or "").strip()
    if tipo_key in DESCONTAR_TIPOS:
        return -qty
    if tipo_key == "modulo_asignado":
        return Decimal("0")
    return qty


def _produccion_cantidad(row) -> int:
    qty = sum(int(v) for v in (row.bonos or {}).values())
    qty += sum(int(getattr(p, "cantidad", 0) or 0) for p in (row.practicas or []))
    qty += sum(int(getattr(i, "cantidad", 0) or 0) for i in (row.internaciones or []))
    return qty


def build_indices(db: Session, *, periodo_id: int) -> IndicesResponse:
    _require_periodo(db, periodo_id)
    detail = build_grid_rows(db, periodo_id=periodo_id, servicio_id=None, q=None, concepto_q=None)

    svc_horas: dict[int, Decimal] = defaultdict(lambda: Decimal("0"))
    svc_monto_cargas: dict[int, Decimal] = defaultdict(lambda: Decimal("0"))
    svc_modulos: dict[int, int] = defaultdict(int)
    svc_profs: dict[int, set[int]] = defaultdict(set)
    svc_names: dict[int, str] = {}

    prof_horas: dict[int, Decimal] = defaultdict(lambda: Decimal("0"))
    prof_modulos: dict[int, int] = defaultdict(int)
    prof_has_carga: set[int] = set()

    for row in detail:
        sid = row.servicio_id
        pid = row.professional_id
        svc_names[sid] = row.servicio_nombre or svc_names.get(sid, "")
        svc_monto_cargas[sid] += Decimal(row.valor or 0)
        svc_profs[sid].add(pid)
        prof_has_carga.add(pid)

        h = signed_horas(row.tipo, row.horas)
        svc_horas[sid] += h
        prof_horas[pid] += h

        if row.tipo == "modulo_asignado":
            svc_modulos[sid] += 1
            prof_modulos[pid] += 1

    ajustes = list(
        db.execute(
            select(NovedadesAjusteCapital).where(
                NovedadesAjusteCapital.periodo_id == periodo_id,
                NovedadesAjusteCapital.deleted_at.is_(None),
                NovedadesAjusteCapital.servicio_id.is_not(None),
            )
        )
        .scalars()
        .all()
    )
    svc_ajustes: dict[int, Decimal] = defaultdict(lambda: Decimal("0"))
    for adj in ajustes:
        assert adj.servicio_id is not None
        svc_ajustes[adj.servicio_id] += Decimal(adj.importe)

    missing_sids = [sid for sid in set(svc_monto_cargas) if sid not in svc_names or not svc_names[sid]]
    if missing_sids:
        for s in db.execute(select(NovedadesServicio).where(NovedadesServicio.id.in_(missing_sids))).scalars().all():
            svc_names[s.id] = s.nombre

    # Activity = ≥1 carga (módulo o novedad), not ajustes alone
    active_svc_ids = set(svc_profs)
    por_servicio = [
        IndicesServicioRow(
            servicio_id=sid,
            servicio_nombre=svc_names.get(sid) or f"#{sid}",
            horas=svc_horas.get(sid, Decimal("0")),
            monto=svc_monto_cargas.get(sid, Decimal("0")) + svc_ajustes.get(sid, Decimal("0")),
            profesionales=len(svc_profs.get(sid, set())),
            modulos=svc_modulos.get(sid, 0),
        )
        for sid in active_svc_ids
    ]
    por_servicio.sort(key=lambda r: (r.servicio_nombre or "").casefold())

    # Professional rows: reuse CH producción (monto + eligibility) + hours/modulos from cargas
    ch_rows = build_capital_humano_rows(db, periodo_id=periodo_id, include_bonos=True)
    ch_by_pid = {r.professional_id: r for r in ch_rows}

    # Include CH-only producción professionals and carga professionals
    prof_ids = set(prof_has_carga) | {
        r.professional_id
        for r in ch_rows
        if Decimal(r.monto_bonos or 0) != 0 or _produccion_cantidad(r) > 0
    }

    professionals: dict[int, NovedadesProfesional] = {}
    if prof_ids:
        professionals = {
            p.id: p
            for p in db.execute(
                select(NovedadesProfesional).where(
                    NovedadesProfesional.id.in_(prof_ids),
                    NovedadesProfesional.deleted_at.is_(None),
                )
            )
            .scalars()
            .all()
        }

    por_profesional: list[IndicesProfesionalRow] = []
    for pid in prof_ids:
        prof = professionals.get(pid)
        if not prof:
            continue
        ch = ch_by_pid.get(pid)
        prod_monto = Decimal(ch.monto_bonos) if ch else Decimal("0")
        prod_qty = _produccion_cantidad(ch) if ch else 0
        # Skip empty ghosts (no cargas and no producción)
        if pid not in prof_has_carga and prod_monto == 0 and prod_qty == 0:
            continue
        por_profesional.append(
            IndicesProfesionalRow(
                professional_id=pid,
                legajo=prof.legajo,
                professional_name=prof.full_name,
                horas=prof_horas.get(pid, Decimal("0")),
                modulos=prof_modulos.get(pid, 0),
                produccion_monto=prod_monto,
                produccion_cantidad=prod_qty,
            )
        )
    por_profesional.sort(key=lambda r: (r.professional_name or "").casefold())

    return IndicesResponse(
        periodo_id=periodo_id,
        por_servicio=por_servicio,
        por_profesional=por_profesional,
    )
