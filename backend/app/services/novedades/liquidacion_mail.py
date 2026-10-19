"""Capital Humano liquidación mail lots (throttled SMTP)."""

from __future__ import annotations

import logging
import re
import threading
import time
from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.novedades import (
    LiquidacionMailItemStatus,
    NovedadesLiquidacionMailItem,
    NovedadesLiquidacionMailLote,
    NovedadesPeriodo,
    NovedadesProfesional,
    PeriodoEstado,
)
from app.models.user import User
from app.schemas.novedades import (
    CapitalHumanoRowResponse,
    LiquidacionMailMissingProfessional,
    LiquidacionMailStatusResponse,
    LiquidacionMailStartResponse,
)
from app.services.email_service import send_email, smtp_configured
from app.services.novedades.capital_humano import build_capital_humano_rows, list_ajustes
from app.services.novedades.export_xls import build_grid_rows

logger = logging.getLogger(__name__)

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_running_lotes: set[int] = set()
_running_lock = threading.Lock()


def is_valid_email(value: str | None) -> bool:
    if not value:
        return False
    text = value.strip()
    if not text or len(text) > 255:
        return False
    return bool(_EMAIL_RE.match(text))


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


def _require_closed_periodo(db: Session, periodo_id: int) -> NovedadesPeriodo:
    periodo = _get_periodo(db, periodo_id)
    if periodo.estado != PeriodoEstado.closed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El envío de liquidaciones solo está disponible con período cerrado",
        )
    return periodo


def _get_lote_for_periodo(db: Session, periodo_id: int) -> NovedadesLiquidacionMailLote | None:
    return db.execute(
        select(NovedadesLiquidacionMailLote).where(
            NovedadesLiquidacionMailLote.periodo_id == periodo_id,
            NovedadesLiquidacionMailLote.deleted_at.is_(None),
        )
    ).scalar_one_or_none()


def _count_by_status(db: Session, lote_id: int) -> dict[str, int]:
    rows = db.execute(
        select(NovedadesLiquidacionMailItem.status, func.count())
        .where(
            NovedadesLiquidacionMailItem.lote_id == lote_id,
            NovedadesLiquidacionMailItem.deleted_at.is_(None),
        )
        .group_by(NovedadesLiquidacionMailItem.status)
    ).all()
    counts = {"pending": 0, "sent": 0, "failed": 0}
    for status_val, n in rows:
        key = str(status_val)
        if key in counts:
            counts[key] = int(n)
    return counts


def _status_response(
    db: Session, *, periodo_id: int, lote: NovedadesLiquidacionMailLote | None
) -> LiquidacionMailStatusResponse:
    if lote is None:
        return LiquidacionMailStatusResponse(
            periodo_id=periodo_id,
            lote_id=None,
            pending=0,
            sent=0,
            failed=0,
            total=0,
            locked=False,
            can_start=True,
            can_retry_failed=False,
            worker_running=False,
        )
    counts = _count_by_status(db, lote.id)
    total = counts["pending"] + counts["sent"] + counts["failed"]
    locked = total > 0 and counts["pending"] == 0 and counts["failed"] == 0 and counts["sent"] == total
    with _running_lock:
        worker_running = lote.id in _running_lotes
    return LiquidacionMailStatusResponse(
        periodo_id=periodo_id,
        lote_id=lote.id,
        pending=counts["pending"],
        sent=counts["sent"],
        failed=counts["failed"],
        total=total,
        locked=locked,
        can_start=False,
        can_retry_failed=counts["failed"] > 0,
        worker_running=worker_running,
    )


def get_mail_status(db: Session, *, periodo_id: int) -> LiquidacionMailStatusResponse:
    _require_closed_periodo(db, periodo_id)
    lote = _get_lote_for_periodo(db, periodo_id)
    return _status_response(db, periodo_id=periodo_id, lote=lote)


def _money(value) -> str:
    try:
        n = Decimal(value)
    except Exception:
        return str(value)
    return f"${n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def build_liquidacion_body(
    *,
    periodo_nombre: str,
    row: CapitalHumanoRowResponse,
    cargas: list,
    ajustes: list,
) -> tuple[str, str]:
    """Return (plain_text, html) for one professional."""
    lines: list[str] = [
        f"Liquidación Novedades — {periodo_nombre}",
        f"Profesional: {row.professional_name}",
        f"Legajo: {row.legajo or '—'}",
        "",
        f"Importe a facturar (Total general): {_money(row.monto_total)}",
        "",
        "Resumen:",
        f"  Total cargas: {_money(row.monto_cargas)}",
        f"  Ajustes: {_money(row.monto_ajustes)}",
        f"  Total producción: {_money(row.monto_bonos)}",
        "",
        "--- Cargas ---",
    ]
    html_parts: list[str] = [
        f"<h2>Liquidación Novedades — {periodo_nombre}</h2>",
        f"<p><strong>Profesional:</strong> {row.professional_name}<br/>",
        f"<strong>Legajo:</strong> {row.legajo or '—'}<br/>",
        f"<strong>Importe a facturar (Total general):</strong> {_money(row.monto_total)}</p>",
        "<p>Total cargas: "
        f"{_money(row.monto_cargas)} · Ajustes: {_money(row.monto_ajustes)} · "
        f"Total producción: {_money(row.monto_bonos)}</p>",
        "<h3>Cargas</h3><ul>",
    ]
    if not cargas:
        lines.append("(sin cargas)")
        html_parts.append("<li>(sin cargas)</li>")
    else:
        for item in cargas:
            concepto = getattr(item, "concepto", None) or "—"
            servicio = getattr(item, "servicio_nombre", None) or "—"
            valor = _money(getattr(item, "valor", None) or 0)
            tipo = getattr(item, "tipo", "") or ""
            line = f"- [{tipo}] {servicio} · {concepto}: {valor}"
            lines.append(line)
            html_parts.append(f"<li>[{tipo}] {servicio} · {concepto}: {valor}</li>")
    html_parts.append("</ul><h3>Producción</h3><ul>")
    lines.extend(["", "--- Producción ---"])
    if row.bonos:
        for key, qty in sorted(row.bonos.items()):
            sub = row.bonos_subtotales.get(key, 0)
            lines.append(f"- Bono {key}: cant {qty} · {_money(sub)}")
            html_parts.append(f"<li>Bono {key}: cant {qty} · {_money(sub)}</li>")
    for p in row.practicas:
        lines.append(
            f"- Práctica {p.centro}/{p.servicio}: cant {p.cantidad} · {_money(p.subtotal)}"
        )
        html_parts.append(
            f"<li>Práctica {p.centro}/{p.servicio}: cant {p.cantidad} · {_money(p.subtotal)}</li>"
        )
    for i in row.internaciones:
        lines.append(f"- Internación {i.sucursal}: cant {i.cantidad} · {_money(i.subtotal)}")
        html_parts.append(
            f"<li>Internación {i.sucursal}: cant {i.cantidad} · {_money(i.subtotal)}</li>"
        )
    if not row.bonos and not row.practicas and not row.internaciones:
        lines.append("(sin producción)")
        html_parts.append("<li>(sin producción)</li>")
    html_parts.append("</ul><h3>Ajustes</h3><ul>")
    lines.extend(["", "--- Ajustes ---"])
    if not ajustes:
        lines.append("(sin ajustes)")
        html_parts.append("<li>(sin ajustes)</li>")
    else:
        for aj in ajustes:
            comentario = getattr(aj, "comentario", None) or "—"
            importe = _money(getattr(aj, "importe", None) or 0)
            lines.append(f"- {comentario}: {importe}")
            html_parts.append(f"<li>{comentario}: {importe}</li>")
    html_parts.append("</ul>")
    return "\n".join(lines), "\n".join(html_parts)


def _send_one(db: Session, item: NovedadesLiquidacionMailItem, periodo: NovedadesPeriodo) -> None:
    rows = build_capital_humano_rows(db, periodo_id=periodo.id, include_bonos=True)
    row = next((r for r in rows if r.professional_id == item.professional_id), None)
    if row is None:
        # Fall back to snapshot totals if professional left the CH list.
        row = CapitalHumanoRowResponse(
            professional_id=item.professional_id,
            legajo=None,
            professional_name=f"Profesional #{item.professional_id}",
            monto_cargas=Decimal("0"),
            monto_ajustes=Decimal("0"),
            monto_bonos=0,
            monto_practicas=0,
            monto_internaciones=0,
            monto_total=Decimal(item.total_general),
        )
    cargas = [
        r
        for r in build_grid_rows(db, periodo_id=periodo.id)
        if r.professional_id == item.professional_id
    ]
    ajustes = list_ajustes(db, periodo_id=periodo.id, professional_id=item.professional_id)
    periodo_nombre = periodo.nombre or f"Período {periodo.id}"
    body_text, body_html = build_liquidacion_body(
        periodo_nombre=periodo_nombre, row=row, cargas=cargas, ajustes=ajustes
    )
    subject = f"Liquidación Novedades — {periodo_nombre}"
    send_email(to_email=item.email, subject=subject, body_text=body_text, body_html=body_html)


def process_lote_pending(db: Session, lote_id: int) -> None:
    lote = db.execute(
        select(NovedadesLiquidacionMailLote).where(
            NovedadesLiquidacionMailLote.id == lote_id,
            NovedadesLiquidacionMailLote.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if not lote:
        return
    periodo = _get_periodo(db, lote.periodo_id)
    delay = max(0.0, float(settings.mail_liquidacion_delay_seconds or 0))
    while True:
        item = db.execute(
            select(NovedadesLiquidacionMailItem)
            .where(
                NovedadesLiquidacionMailItem.lote_id == lote_id,
                NovedadesLiquidacionMailItem.status == LiquidacionMailItemStatus.pending.value,
                NovedadesLiquidacionMailItem.deleted_at.is_(None),
            )
            .order_by(NovedadesLiquidacionMailItem.id)
            .limit(1)
        ).scalar_one_or_none()
        if not item:
            break
        try:
            _send_one(db, item, periodo)
            item.status = LiquidacionMailItemStatus.sent.value
            item.error_message = None
            item.sent_at = datetime.utcnow()
            item.updated_at = datetime.utcnow()
            db.commit()
        except Exception as exc:
            logger.exception("Liquidación mail failed item_id=%s", item.id)
            item.status = LiquidacionMailItemStatus.failed.value
            item.error_message = str(exc)[:500]
            item.updated_at = datetime.utcnow()
            db.commit()
        if delay:
            time.sleep(delay)


def _worker(lote_id: int) -> None:
    db = SessionLocal()
    try:
        process_lote_pending(db, lote_id)
    finally:
        db.close()
        with _running_lock:
            _running_lotes.discard(lote_id)


def start_lote_worker(lote_id: int) -> None:
    with _running_lock:
        if lote_id in _running_lotes:
            return
        _running_lotes.add(lote_id)
    thread = threading.Thread(target=_worker, args=(lote_id,), daemon=True, name=f"mail-lote-{lote_id}")
    thread.start()


def start_mail_lot(db: Session, *, periodo_id: int, user: User) -> LiquidacionMailStartResponse:
    if not smtp_configured():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="SMTP no configurado",
        )
    periodo = _require_closed_periodo(db, periodo_id)
    existing = _get_lote_for_periodo(db, periodo_id)
    if existing is not None:
        st = _status_response(db, periodo_id=periodo_id, lote=existing)
        if st.locked:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El período ya tiene un lote de mails completo; no se puede reenviar",
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un lote para este período; usá Reintentar fallidos si corresponde",
        )

    rows = build_capital_humano_rows(db, periodo_id=periodo_id, include_bonos=True)
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No hay profesionales en Capital Humano para este período",
        )

    prof_ids = [r.professional_id for r in rows]
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
    missing: list[LiquidacionMailMissingProfessional] = []
    for r in rows:
        prof = professionals.get(r.professional_id)
        email = getattr(prof, "email", None) if prof else None
        if not is_valid_email(email):
            missing.append(
                LiquidacionMailMissingProfessional(
                    professional_id=r.professional_id,
                    legajo=r.legajo,
                    professional_name=r.professional_name,
                    email=email,
                )
            )
    if missing:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "missing_emails",
                "message": "Hay profesionales sin mail válido; el lote está bloqueado",
                "missing_emails": [m.model_dump() for m in missing],
            },
        )

    now = datetime.utcnow()
    lote = NovedadesLiquidacionMailLote(
        periodo_id=periodo.id,
        created_at=now,
        updated_at=now,
        created_by=user.id,
        updated_by=user.id,
        deleted_at=None,
    )
    db.add(lote)
    db.flush()
    for r in rows:
        prof = professionals[r.professional_id]
        db.add(
            NovedadesLiquidacionMailItem(
                lote_id=lote.id,
                professional_id=r.professional_id,
                email=str(prof.email).strip(),
                total_general=Decimal(r.monto_total),
                status=LiquidacionMailItemStatus.pending.value,
                created_at=now,
                updated_at=now,
                created_by=user.id,
                updated_by=user.id,
                deleted_at=None,
            )
        )
    db.commit()
    db.refresh(lote)
    start_lote_worker(lote.id)
    return LiquidacionMailStartResponse(
        lote_id=lote.id,
        periodo_id=periodo.id,
        total=len(rows),
        status=_status_response(db, periodo_id=periodo.id, lote=lote),
    )


def retry_failed(db: Session, *, periodo_id: int, user: User) -> LiquidacionMailStatusResponse:
    if not smtp_configured():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="SMTP no configurado",
        )
    _require_closed_periodo(db, periodo_id)
    lote = _get_lote_for_periodo(db, periodo_id)
    if lote is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay lote para este período")
    st = _status_response(db, periodo_id=periodo_id, lote=lote)
    if st.locked:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El lote está completo; no se puede reenviar",
        )
    if st.failed == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No hay destinatarios fallidos para reintentar",
        )
    now = datetime.utcnow()
    items = list(
        db.execute(
            select(NovedadesLiquidacionMailItem).where(
                NovedadesLiquidacionMailItem.lote_id == lote.id,
                NovedadesLiquidacionMailItem.status == LiquidacionMailItemStatus.failed.value,
                NovedadesLiquidacionMailItem.deleted_at.is_(None),
            )
        )
        .scalars()
        .all()
    )
    for item in items:
        item.status = LiquidacionMailItemStatus.pending.value
        item.error_message = None
        item.updated_at = now
        item.updated_by = user.id
    lote.updated_at = now
    lote.updated_by = user.id
    db.commit()
    start_lote_worker(lote.id)
    return _status_response(db, periodo_id=periodo_id, lote=lote)
