"""Recalc persisted module/novedad importes from current catalog rates."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.novedades import (
    NovedadesAsignacionModulo,
    NovedadesModulo,
    NovedadesNovedad,
    NovedadesPeriodo,
    NovedadesProfesional,
    NovedadesServicio,
)
from app.models.user import User
from app.schemas.novedades import (
    RecalculoApplyResponse,
    RecalculoHorasBlock,
    RecalculoModuloRow,
    RecalculoPreviewResponse,
    RecalculoRequest,
)
from app.services.novedades.helpers import novedad_valor_calculado
from app.services.novedades.prof_sync import modulo_valor_para_profesional

RecalculoModo = Literal["horas", "modulos", "ambos"]


def _get_periodo(db: Session, periodo_id: int) -> NovedadesPeriodo:
    periodo = db.execute(
        select(NovedadesPeriodo).where(
            NovedadesPeriodo.id == periodo_id,
            NovedadesPeriodo.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if not periodo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Periodo no encontrado")
    return periodo


def _money_eq(a: Decimal, b: Decimal) -> bool:
    return Decimal(a).quantize(Decimal("0.01")) == Decimal(b).quantize(Decimal("0.01"))


def _load_asignaciones(db: Session, periodo_id: int) -> list[NovedadesAsignacionModulo]:
    return list(
        db.execute(
            select(NovedadesAsignacionModulo).where(
                NovedadesAsignacionModulo.periodo_id == periodo_id,
                NovedadesAsignacionModulo.deleted_at.is_(None),
            )
        )
        .scalars()
        .all()
    )


def _load_novedades(db: Session, periodo_id: int) -> list[NovedadesNovedad]:
    return list(
        db.execute(
            select(NovedadesNovedad).where(
                NovedadesNovedad.periodo_id == periodo_id,
                NovedadesNovedad.deleted_at.is_(None),
            )
        )
        .scalars()
        .all()
    )


def _compute_preview(db: Session, *, periodo_id: int, modo: RecalculoModo) -> RecalculoPreviewResponse:
    _get_periodo(db, periodo_id)
    include_modulos = modo in ("modulos", "ambos")
    include_horas = modo in ("horas", "ambos")

    modulo_rows: list[RecalculoModuloRow] = []
    modulos_changed = 0
    horas_block = RecalculoHorasBlock(importe_actual=Decimal("0"), importe_nuevo=Decimal("0"), filas=0, filas_cambio=0)
    has_changes = False

    if include_modulos:
        asignaciones = _load_asignaciones(db, periodo_id)
        modulo_ids = {a.modulo_id for a in asignaciones}
        prof_ids = {a.professional_id for a in asignaciones}
        servicio_ids = {a.servicio_id for a in asignaciones}
        modulos = {
            m.id: m
            for m in db.execute(
                select(NovedadesModulo).where(NovedadesModulo.id.in_(modulo_ids or [-1]))
            )
            .scalars()
            .all()
        }
        professionals = {
            p.id: p
            for p in db.execute(
                select(NovedadesProfesional).where(NovedadesProfesional.id.in_(prof_ids or [-1]))
            )
            .scalars()
            .all()
        }
        servicios = {
            s.id: s
            for s in db.execute(
                select(NovedadesServicio).where(NovedadesServicio.id.in_(servicio_ids or [-1]))
            )
            .scalars()
            .all()
        }
        by_mod: dict[int, dict] = {}
        for a in asignaciones:
            mod = modulos.get(a.modulo_id)
            prof = professionals.get(a.professional_id)
            svc = servicios.get(a.servicio_id)
            if not mod or not prof or not svc:
                continue
            nuevo = modulo_valor_para_profesional(
                Decimal(mod.valor),
                es_especialista=bool(prof.es_especialista),
                servicio_especialista=bool(getattr(svc, "especialista", False)),
            )
            actual = Decimal(a.valor)
            bucket = by_mod.setdefault(
                a.modulo_id,
                {
                    "descripcion": mod.descripcion,
                    "filas": 0,
                    "filas_cambio": 0,
                    "importe_actual": Decimal("0"),
                    "importe_nuevo": Decimal("0"),
                },
            )
            bucket["filas"] += 1
            bucket["importe_actual"] += actual
            bucket["importe_nuevo"] += nuevo
            if not _money_eq(actual, nuevo):
                bucket["filas_cambio"] += 1
                modulos_changed += 1
                has_changes = True
        for mid, b in sorted(by_mod.items(), key=lambda x: (x[1]["descripcion"] or "").lower()):
            modulo_rows.append(
                RecalculoModuloRow(
                    modulo_id=mid,
                    descripcion=b["descripcion"],
                    filas=b["filas"],
                    filas_cambio=b["filas_cambio"],
                    importe_actual=b["importe_actual"],
                    importe_nuevo=b["importe_nuevo"],
                )
            )

    if include_horas:
        novedades = _load_novedades(db, periodo_id)
        servicio_ids = {n.servicio_id for n in novedades}
        servicios = {
            s.id: s
            for s in db.execute(
                select(NovedadesServicio).where(NovedadesServicio.id.in_(servicio_ids or [-1]))
            )
            .scalars()
            .all()
        }
        actual_sum = Decimal("0")
        nuevo_sum = Decimal("0")
        filas_cambio = 0
        for n in novedades:
            svc = servicios.get(n.servicio_id)
            if not svc:
                continue
            actual = Decimal(getattr(n, "valor", None) or 0)
            nuevo = novedad_valor_calculado(n.tipo, n.horas, svc.valor_hora or 0)
            actual_sum += actual
            nuevo_sum += nuevo
            if not _money_eq(actual, nuevo):
                filas_cambio += 1
                has_changes = True
        horas_block = RecalculoHorasBlock(
            importe_actual=actual_sum,
            importe_nuevo=nuevo_sum,
            filas=len(novedades),
            filas_cambio=filas_cambio,
        )

    return RecalculoPreviewResponse(
        periodo_id=periodo_id,
        modo=modo,
        has_changes=has_changes,
        modulos=modulo_rows,
        horas=horas_block if include_horas else None,
        filas_cambio_modulos=modulos_changed,
        filas_cambio_horas=horas_block.filas_cambio if include_horas else 0,
    )


def preview_recalculo(db: Session, payload: RecalculoRequest, user: User) -> RecalculoPreviewResponse:
    _ = user
    return _compute_preview(db, periodo_id=payload.periodo_id, modo=payload.modo)


def apply_recalculo(db: Session, payload: RecalculoRequest, user: User) -> RecalculoApplyResponse:
    preview = _compute_preview(db, periodo_id=payload.periodo_id, modo=payload.modo)
    if not preview.has_changes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No hay cambios: los importes ya coinciden con el catálogo actual",
        )

    now = datetime.utcnow()
    updated_modulos = 0
    updated_horas = 0
    modo = payload.modo

    if modo in ("modulos", "ambos"):
        asignaciones = _load_asignaciones(db, payload.periodo_id)
        modulo_ids = {a.modulo_id for a in asignaciones}
        prof_ids = {a.professional_id for a in asignaciones}
        servicio_ids = {a.servicio_id for a in asignaciones}
        modulos = {
            m.id: m
            for m in db.execute(select(NovedadesModulo).where(NovedadesModulo.id.in_(modulo_ids or [-1])))
            .scalars()
            .all()
        }
        professionals = {
            p.id: p
            for p in db.execute(
                select(NovedadesProfesional).where(NovedadesProfesional.id.in_(prof_ids or [-1]))
            )
            .scalars()
            .all()
        }
        servicios = {
            s.id: s
            for s in db.execute(
                select(NovedadesServicio).where(NovedadesServicio.id.in_(servicio_ids or [-1]))
            )
            .scalars()
            .all()
        }
        for a in asignaciones:
            mod = modulos.get(a.modulo_id)
            prof = professionals.get(a.professional_id)
            svc = servicios.get(a.servicio_id)
            if not mod or not prof or not svc:
                continue
            nuevo = modulo_valor_para_profesional(
                Decimal(mod.valor),
                es_especialista=bool(prof.es_especialista),
                servicio_especialista=bool(getattr(svc, "especialista", False)),
            )
            if _money_eq(Decimal(a.valor), nuevo):
                continue
            a.valor = nuevo
            a.updated_at = now
            a.updated_by = user.id
            updated_modulos += 1

    if modo in ("horas", "ambos"):
        novedades = _load_novedades(db, payload.periodo_id)
        servicio_ids = {n.servicio_id for n in novedades}
        servicios = {
            s.id: s
            for s in db.execute(
                select(NovedadesServicio).where(NovedadesServicio.id.in_(servicio_ids or [-1]))
            )
            .scalars()
            .all()
        }
        for n in novedades:
            svc = servicios.get(n.servicio_id)
            if not svc:
                continue
            nuevo = novedad_valor_calculado(n.tipo, n.horas, svc.valor_hora or 0)
            actual = Decimal(getattr(n, "valor", None) or 0)
            if _money_eq(actual, nuevo):
                continue
            n.valor = nuevo
            n.updated_at = now
            n.updated_by = user.id
            updated_horas += 1

    db.commit()
    return RecalculoApplyResponse(
        periodo_id=payload.periodo_id,
        modo=modo,
        updated_modulos=updated_modulos,
        updated_horas=updated_horas,
        preview=preview,
    )
