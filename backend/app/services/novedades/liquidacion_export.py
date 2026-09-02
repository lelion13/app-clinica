"""Export liquidación XLS for Capital Humano (closed periods only)."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from io import BytesIO

from fastapi import HTTPException, status
from openpyxl import Workbook
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.novedades import (
    NovedadesAjusteCapital,
    NovedadesPeriodo,
    NovedadesProfesional,
    NovedadesServicio,
    PeriodoEstado,
)
from app.services.novedades.capital_humano import SPECIAL_BONO_SERVICIOS
from app.services.novedades.export_xls import build_grid_rows
from app.services.novedades.produccion_tarifas import (
    load_tarifas_by_opcion_key,
    valorize_bonos,
    valorize_internaciones,
    valorize_practicas,
)


def _is_special_bono_key(key: str) -> bool:
    parts = str(key).split("|")
    return len(parts) >= 2 and parts[1] in SPECIAL_BONO_SERVICIOS


def _filter_eligible_bonos(bonos: dict[str, int], has_modulo: bool) -> dict[str, int]:
    if has_modulo:
        return bonos
    return {k: v for k, v in bonos.items() if _is_special_bono_key(k)}

# Fixed conceptos when professional has no cargas but has special bonos.
# (empresa, service_group) -> concepto
# service_group: "dea_cai" | "dep_cap"
FIXED_CONCEPTOS = {
    ("CMG", "dea_cai"): 90,
    ("CMG", "dep_cap"): 91,
    ("CHI", "dea_cai"): 123,
    ("CHI", "dep_cap"): 122,
}

DEA_CAI = {"DEA", "CAI"}
DEP_CAP = {"DEP", "CAP"}


@dataclass
class LiquidacionRow:
    empresa: str
    legajo: str
    monto: Decimal
    concepto: int


def empresa_from_concepto(concepto: int) -> str:
    return "CHI" if int(concepto) > 100 else "CMG"


def empresa_from_prefix(raw: str | None) -> str:
    text = str(raw or "").strip().upper()
    if text.startswith("SC"):
        return "CHI"
    return "CMG"


def _service_group(servicio: str) -> str | None:
    s = str(servicio or "").strip().upper()
    if s in DEA_CAI:
        return "dea_cai"
    if s in DEP_CAP:
        return "dep_cap"
    return None


def _split_equal(amount: Decimal, targets: list[int]) -> dict[int, Decimal]:
    """Split amount equally across concepto targets."""
    if not targets or amount == 0:
        return {}
    n = len(targets)
    share = amount / Decimal(n)
    return {c: share for c in targets}


def _add_to(bucket: dict[int, Decimal], additions: dict[int, Decimal]) -> None:
    for concepto, monto in additions.items():
        bucket[concepto] = bucket.get(concepto, Decimal("0")) + Decimal(monto)


def build_liquidacion_rows(db: Session, *, periodo_id: int) -> list[LiquidacionRow]:
    periodo = db.execute(
        select(NovedadesPeriodo).where(NovedadesPeriodo.id == periodo_id, NovedadesPeriodo.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not periodo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Periodo no encontrado")
    if periodo.estado != PeriodoEstado.closed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Solo se puede exportar liquidacion de periodos cerrados",
        )

    detail = build_grid_rows(db, periodo_id=periodo_id)
    servicio_ids = {row.servicio_id for row in detail}
    servicios: dict[int, NovedadesServicio] = {}
    if servicio_ids:
        servicios = {
            s.id: s
            for s in db.execute(
                select(NovedadesServicio).where(NovedadesServicio.id.in_(servicio_ids))
            )
            .scalars()
            .all()
        }

    missing_servicios: list[str] = []
    seen_missing: set[int] = set()
    for row in detail:
        svc = servicios.get(row.servicio_id)
        if not svc:
            continue
        if svc.concepto_liquidacion is None and svc.id not in seen_missing:
            seen_missing.add(svc.id)
            missing_servicios.append(svc.nombre or f"#{svc.id}")
    if missing_servicios:
        names = ", ".join(sorted(missing_servicios))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"No se puede exportar: servicios sin concepto de liquidacion: {names}",
        )

    # cargas: professional_id -> concepto -> monto
    cargas: dict[int, dict[int, Decimal]] = defaultdict(lambda: defaultdict(lambda: Decimal("0")))
    has_modulos: set[int] = set()
    for row in detail:
        svc = servicios.get(row.servicio_id)
        if not svc or svc.concepto_liquidacion is None:
            continue
        concepto = int(svc.concepto_liquidacion)
        cargas[row.professional_id][concepto] += Decimal(row.valor or 0)
        if getattr(row, "tipo", None) == "modulo_asignado":
            has_modulos.add(row.professional_id)

    # ajustes
    ajustes = list(
        db.execute(
            select(NovedadesAjusteCapital).where(
                NovedadesAjusteCapital.periodo_id == periodo_id,
                NovedadesAjusteCapital.deleted_at.is_(None),
            )
        )
        .scalars()
        .all()
    )
    ajustes_by_prof: dict[int, Decimal] = defaultdict(lambda: Decimal("0"))
    for item in ajustes:
        ajustes_by_prof[item.professional_id] += Decimal(item.importe)

    from app.services.novedades.bonos_import import (
        load_bonos_snapshot,
        load_internaciones_snapshot,
        load_practicas_snapshot,
    )

    _, bonos_by_prof = load_bonos_snapshot(db, periodo_id=periodo_id)
    practicas_by_prof = load_practicas_snapshot(db, periodo_id=periodo_id)
    internaciones_by_prof = load_internaciones_snapshot(db, periodo_id=periodo_id)
    tarifas = load_tarifas_by_opcion_key(db)

    prof_ids = (
        set(cargas)
        | set(ajustes_by_prof)
        | set(bonos_by_prof)
        | set(practicas_by_prof)
        | set(internaciones_by_prof)
    )
    if not prof_ids:
        return []

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

    # Accumulator: professional_id -> concepto -> monto
    out: dict[int, dict[int, Decimal]] = defaultdict(lambda: defaultdict(lambda: Decimal("0")))

    for pid in prof_ids:
        prof = professionals.get(pid)
        if not prof:
            continue

        has_modulo = pid in has_modulos
        carga_conceptos = dict(cargas.get(pid, {}))

        # Start with carga amounts
        for concepto, monto in carga_conceptos.items():
            out[pid][concepto] += monto

        raw_bonos = bonos_by_prof.get(pid, {})
        eligible_bonos = _filter_eligible_bonos(raw_bonos, has_modulo)
        bonos_subtotales, _ = valorize_bonos(eligible_bonos, tarifas)

        raw_practicas = practicas_by_prof.get(pid, [])
        eligible_practicas = [
            p for p in raw_practicas if has_modulo or p.get("servicio") in SPECIAL_BONO_SERVICIOS
        ]
        practicas_items, _ = valorize_practicas(eligible_practicas, tarifas)

        qualifies_internacion = has_modulo or bool(eligible_bonos) or bool(eligible_practicas)
        raw_internaciones = internaciones_by_prof.get(pid, [])
        eligible_internaciones = raw_internaciones if qualifies_internacion else []
        internaciones_items, _ = valorize_internaciones(eligible_internaciones, tarifas)

        # Production buckets by empresa
        prod_by_empresa: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
        for key, subtotal in bonos_subtotales.items():
            parts = str(key).split("|")
            centro = parts[0] if parts else ""
            prod_by_empresa[empresa_from_prefix(centro)] += Decimal(subtotal)
        for p in practicas_items:
            prod_by_empresa[empresa_from_prefix(p.get("centro"))] += Decimal(p.get("subtotal", 0))
        for i in internaciones_items:
            prod_by_empresa[empresa_from_prefix(i.get("sucursal"))] += Decimal(i.get("subtotal", 0))

        if carga_conceptos:
            conceptos_list = list(carga_conceptos.keys())
            by_emp: dict[str, list[int]] = {"CMG": [], "CHI": []}
            for c in conceptos_list:
                by_emp[empresa_from_concepto(c)].append(c)

            for emp, amount in prod_by_empresa.items():
                if amount == 0:
                    continue
                targets = by_emp.get(emp) or conceptos_list
                _add_to(out[pid], _split_equal(amount, targets))

            ajuste = ajustes_by_prof.get(pid, Decimal("0"))
            if ajuste:
                _add_to(out[pid], _split_equal(ajuste, conceptos_list))
            continue

        # No cargas: only export if special bonos DEA/DEP/CAP/CAI
        special_keys = [k for k in eligible_bonos if _is_special_bono_key(k)]
        if not special_keys:
            # No fixed conceptos → omit professional (and their ajustes)
            if pid in out and not out[pid]:
                del out[pid]
            continue

        fixed_present: set[int] = set()
        for key in special_keys:
            parts = str(key).split("|")
            if len(parts) < 2:
                continue
            emp = empresa_from_prefix(parts[0])
            group = _service_group(parts[1])
            if not group:
                continue
            concepto = FIXED_CONCEPTOS.get((emp, group))
            if concepto is not None:
                fixed_present.add(concepto)

        if not fixed_present:
            continue

        fixed_list = sorted(fixed_present)
        # Ensure rows exist even with zero carga base
        for c in fixed_list:
            out[pid][c] += Decimal("0")

        fixed_by_emp: dict[str, list[int]] = {"CMG": [], "CHI": []}
        for c in fixed_list:
            fixed_by_emp[empresa_from_concepto(c)].append(c)

        for emp, amount in prod_by_empresa.items():
            if amount == 0:
                continue
            targets = fixed_by_emp.get(emp) or fixed_list
            _add_to(out[pid], _split_equal(amount, targets))

        ajuste = ajustes_by_prof.get(pid, Decimal("0"))
        if ajuste:
            _add_to(out[pid], _split_equal(ajuste, fixed_list))

    # Aggregate to (empresa, legajo, concepto)
    aggregated: dict[tuple[str, str, int], Decimal] = defaultdict(lambda: Decimal("0"))
    for pid, conceptos in out.items():
        prof = professionals.get(pid)
        if not prof:
            continue
        legajo = "" if prof.legajo is None else str(prof.legajo)
        for concepto, monto in conceptos.items():
            if monto == 0:
                continue
            emp = empresa_from_concepto(concepto)
            aggregated[(emp, legajo, concepto)] += monto

    rows = [
        LiquidacionRow(empresa=emp, legajo=legajo, monto=monto, concepto=concepto)
        for (emp, legajo, concepto), monto in aggregated.items()
    ]
    rows.sort(key=lambda r: (r.empresa, r.legajo, r.concepto))
    return rows


def export_liquidacion_xlsx_bytes(db: Session, *, periodo_id: int) -> bytes:
    rows = build_liquidacion_rows(db, periodo_id=periodo_id)
    wb = Workbook()
    ws = wb.active
    ws.title = "Liquidacion"
    ws.append(["empresa", "legajo", "monto", "concepto"])
    for row in rows:
        ws.append([row.empresa, row.legajo, float(row.monto), row.concepto])
    buffer = BytesIO()
    wb.save(buffer)
    return buffer.getvalue()
