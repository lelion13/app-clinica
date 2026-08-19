from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.novedades import (
    NovedadesAjusteCapital,
    NovedadesPeriodo,
    NovedadesProfesional,
)
from app.models.user import User
from app.schemas.novedades import (
    AjusteCapitalCreateRequest,
    AjusteCapitalResponse,
    BonoColumnaResponse,
    CapitalHumanoGridResponse,
    CapitalHumanoRowResponse,
)
from app.services.novedades.export_xls import build_grid_rows
from app.services.novedades.helpers import get_professional_or_404, get_servicio_or_404
from app.services.novedades.produccion_tarifas import load_tarifas_by_opcion_key, valorize_bonos

SPECIAL_BONO_SERVICIOS = {"DEA", "DEP", "CAP", "CAI"}


def has_special_bono_service(bonos: dict[str, int] | None) -> bool:
    """True when any bonus option belongs to special service set."""
    if not bonos:
        return False
    for key in bonos:
        parts = str(key).split("|")
        if len(parts) != 4:
            continue
        if parts[1] in SPECIAL_BONO_SERVICIOS:
            return True
    return False


def build_capital_humano_rows(
    db: Session,
    *,
    periodo_id: int | None = None,
    servicio_id: int | None = None,
    q: str | None = None,
    include_bonos: bool = False,
    tarifas: dict[str, int] | None = None,
) -> list[CapitalHumanoRowResponse]:
    detail = build_grid_rows(db, periodo_id=periodo_id, servicio_id=servicio_id, q=None, concepto_q=None)
    cargas_by_prof: dict[int, Decimal] = {}
    for row in detail:
        cargas_by_prof[row.professional_id] = cargas_by_prof.get(row.professional_id, Decimal("0")) + (
            row.valor or Decimal("0")
        )

    ajustes_q = select(NovedadesAjusteCapital).where(NovedadesAjusteCapital.deleted_at.is_(None))
    if periodo_id is not None:
        ajustes_q = ajustes_q.where(NovedadesAjusteCapital.periodo_id == periodo_id)
    if servicio_id is not None:
        ajustes_q = ajustes_q.where(NovedadesAjusteCapital.servicio_id == servicio_id)
    else:
        # Sin filtro de servicio: incluir ajustes globales (servicio_id NULL) y por servicio.
        pass
    ajustes = list(db.execute(ajustes_q).scalars().all())
    ajustes_by_prof: dict[int, Decimal] = {}
    for item in ajustes:
        ajustes_by_prof[item.professional_id] = ajustes_by_prof.get(item.professional_id, Decimal("0")) + Decimal(
            item.importe
        )

    prof_ids = set(cargas_by_prof) | set(ajustes_by_prof)

    bonos_by_prof: dict[int, dict[str, int]] = {}
    if include_bonos:
        from app.services.novedades.bonos_import import load_bonos_snapshot

        _, bonos_by_prof = load_bonos_snapshot(db, periodo_id=periodo_id)
        # Promote bonus-only professionals for DEA/DEP/CAP/CAI.
        prof_ids |= {pid for pid, bonos in bonos_by_prof.items() if has_special_bono_service(bonos)}

    if tarifas is None and include_bonos:
        tarifas = load_tarifas_by_opcion_key(db)
    elif tarifas is None:
        tarifas = {}

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

    needle = (q or "").strip().lower()
    rows: list[CapitalHumanoRowResponse] = []
    for pid in prof_ids:
        prof = professionals.get(pid)
        if not prof:
            continue
        if needle:
            hay = f"{prof.full_name} {prof.legajo or ''} {prof.codprof}".lower()
            if needle not in hay:
                continue
        monto_cargas = cargas_by_prof.get(pid, Decimal("0"))
        monto_ajustes = ajustes_by_prof.get(pid, Decimal("0"))
        prof_bonos = bonos_by_prof.get(pid, {})
        bonos_subtotales, monto_bonos = valorize_bonos(prof_bonos, tarifas)
        monto_total = monto_cargas + monto_ajustes + Decimal(monto_bonos)
        rows.append(
            CapitalHumanoRowResponse(
                professional_id=pid,
                legajo=prof.legajo,
                professional_name=prof.full_name,
                monto_cargas=monto_cargas,
                monto_ajustes=monto_ajustes,
                monto_bonos=monto_bonos,
                monto_total=monto_total,
                bonos=prof_bonos,
                bonos_subtotales=bonos_subtotales,
            )
        )
    rows.sort(key=lambda r: (r.professional_name or "").lower())
    return rows


def _expand_bono_columns(
    base_columns: list[BonoColumnaResponse], tarifas: dict[str, int]
) -> tuple[list[BonoColumnaResponse], list[str]]:
    expanded: list[BonoColumnaResponse] = []
    sin_tarifa: list[str] = []
    for col in base_columns:
        expanded.append(
            BonoColumnaResponse(
                key=col.key,
                label=col.label,
                centro=col.centro,
                servicio=col.servicio,
                semana=col.semana,
                horario=col.horario,
                kind="cantidad",
                opcion_key=col.key,
            )
        )
        expanded.append(
            BonoColumnaResponse(
                key=f"{col.key}|$",
                label=f"{col.label} · $",
                centro=col.centro,
                servicio=col.servicio,
                semana=col.semana,
                horario=col.horario,
                kind="subtotal",
                opcion_key=col.key,
            )
        )
        if col.key not in tarifas:
            sin_tarifa.append(col.key)
    return expanded, sin_tarifa


def build_capital_humano_grid(
    db: Session,
    *,
    periodo_id: int | None = None,
    servicio_id: int | None = None,
    q: str | None = None,
) -> CapitalHumanoGridResponse:
    from app.services.novedades.bonos_import import load_bonos_snapshot

    base_columns, _ = load_bonos_snapshot(db, periodo_id=periodo_id)
    tarifas = load_tarifas_by_opcion_key(db)
    columns, opciones_sin_tarifa = _expand_bono_columns(base_columns, tarifas)
    rows = build_capital_humano_rows(
        db,
        periodo_id=periodo_id,
        servicio_id=servicio_id,
        q=q,
        include_bonos=True,
        tarifas=tarifas,
    )
    return CapitalHumanoGridResponse(columns=columns, rows=rows, opciones_sin_tarifa=opciones_sin_tarifa)

def list_ajustes(
    db: Session,
    *,
    professional_id: int,
    periodo_id: int,
    servicio_id: int | None = None,
) -> list[AjusteCapitalResponse]:
    query = select(NovedadesAjusteCapital).where(
        NovedadesAjusteCapital.deleted_at.is_(None),
        NovedadesAjusteCapital.professional_id == professional_id,
        NovedadesAjusteCapital.periodo_id == periodo_id,
    )
    if servicio_id is not None:
        query = query.where(NovedadesAjusteCapital.servicio_id == servicio_id)
    items = list(db.execute(query.order_by(NovedadesAjusteCapital.id.desc())).scalars().all())
    return [_ajuste_response(db, item) for item in items]


def create_ajuste(db: Session, payload: AjusteCapitalCreateRequest, user: User) -> AjusteCapitalResponse:
    if payload.importe == 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El importe no puede ser 0")
    comentario = (payload.comentario or "").strip()
    if not comentario:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El comentario es obligatorio")

    periodo = db.execute(
        select(NovedadesPeriodo).where(NovedadesPeriodo.id == payload.periodo_id, NovedadesPeriodo.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not periodo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Periodo no encontrado")

    get_professional_or_404(db, payload.professional_id)
    if payload.servicio_id is not None:
        get_servicio_or_404(db, payload.servicio_id)

    now = datetime.utcnow()
    item = NovedadesAjusteCapital(
        professional_id=payload.professional_id,
        periodo_id=payload.periodo_id,
        servicio_id=payload.servicio_id,
        importe=payload.importe,
        comentario=comentario[:500],
        created_at=now,
        updated_at=now,
        created_by=user.id,
        updated_by=user.id,
        deleted_at=None,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return _ajuste_response(db, item)


def _ajuste_response(db: Session, item: NovedadesAjusteCapital) -> AjusteCapitalResponse:
    actor = None
    if item.created_by:
        actor = db.execute(select(User).where(User.id == item.created_by)).scalar_one_or_none()
    return AjusteCapitalResponse(
        id=item.id,
        professional_id=item.professional_id,
        periodo_id=item.periodo_id,
        servicio_id=item.servicio_id,
        importe=item.importe,
        comentario=item.comentario,
        created_at=item.created_at,
        created_by=item.created_by,
        created_by_name=actor.name if actor else None,
    )


def export_capital_xlsx_bytes(
    db: Session,
    *,
    periodo_id: int | None = None,
    servicio_id: int | None = None,
    q: str | None = None,
) -> bytes:
    from io import BytesIO

    from openpyxl import Workbook

    rows = build_capital_humano_rows(
        db, periodo_id=periodo_id, servicio_id=servicio_id, q=q, include_bonos=True
    )
    wb = Workbook()
    ws = wb.active
    ws.title = "Capital Humano"
    ws.append(["legajo", "profesional", "monto_cargas", "monto_ajustes", "monto_total"])
    for row in rows:
        ws.append(
            [
                row.legajo,
                row.professional_name,
                float(row.monto_cargas),
                float(row.monto_ajustes),
                float(row.monto_total),
            ]
        )
    buffer = BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def export_capital_bonos_xlsx_bytes(
    db: Session,
    *,
    periodo_id: int | None = None,
    servicio_id: int | None = None,
    q: str | None = None,
) -> bytes:
    from io import BytesIO

    from openpyxl import Workbook

    grid = build_capital_humano_grid(db, periodo_id=periodo_id, servicio_id=servicio_id, q=q)
    wb = Workbook()
    ws = wb.active
    ws.title = "Capital Humano Bonos"
    headers = ["legajo", "profesional", "monto_cargas", "monto_ajustes", "monto_total"] + [
        col.label for col in grid.columns
    ]
    ws.append(headers)
    for row in grid.rows:
        values = [
            row.legajo,
            row.professional_name,
            float(row.monto_cargas),
            float(row.monto_ajustes),
            float(row.monto_total),
        ]
        for col in grid.columns:
            opcion_key = col.opcion_key or col.key
            if col.kind == "subtotal":
                values.append(row.bonos_subtotales.get(opcion_key, 0))
            else:
                values.append(row.bonos.get(opcion_key, 0))
        ws.append(values)
    buffer = BytesIO()
    wb.save(buffer)
    return buffer.getvalue()