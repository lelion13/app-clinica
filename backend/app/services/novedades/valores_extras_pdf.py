"""PDF Valores Extras — chrome visual alineado a app-recepcion (reglamento / firmas)."""

from __future__ import annotations

import logging
import re
from decimal import Decimal
from io import BytesIO
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.schemas.novedades import ValoresExtrasProfesionalRow, ValoresExtrasResponse

logger = logging.getLogger(__name__)

_ASSETS = Path(__file__).resolve().parent.parent.parent / "assets"
_HEADER_BAND = _ASSETS / "pdf-header-band.png"

_NAVY = colors.HexColor("#153e6d")
_TITLE_BG = colors.HexColor("#ededed")
_TITLE_FG = colors.HexColor("#0f2147")
_BODY_FG = colors.HexColor("#0f2147")
_MUTED = colors.HexColor("#555555")
_LINE = colors.HexColor("#d0d0d0")

_PAGE_W, _PAGE_H = A4
_HEADER_H = 124.5
_TITLE_BAND_H = 70.0
_CONTENT_TOP = _HEADER_H + _TITLE_BAND_H
_FOOTER_Y = 28.0
_SIDE = 45.5

_DOC_TITLE = "Valores Extras"
_FOOTER_LABEL = "Valores Extras"
_SAFE = re.compile(r"[^\w.\-]+", re.UNICODE)


def _safe_token(value: str | None, fallback: str) -> str:
    raw = (value or "").strip()
    if not raw:
        return fallback
    cleaned = _SAFE.sub("_", raw).strip("._-")
    return cleaned[:80] or fallback


def build_filename(*, periodo_nombre: str | None, periodo_id: int) -> str:
    period = _safe_token(periodo_nombre, f"periodo_{periodo_id}")
    return f"Valores_Extras_{period}.pdf"


def _money(value: Decimal | None) -> str:
    n = Decimal(value or 0)
    return f"$ {n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _qty(value: Decimal | None) -> str:
    if value is None:
        return "—"
    n = Decimal(value)
    if n == n.to_integral_value():
        return str(int(n))
    return f"{n:.2f}".rstrip("0").rstrip(".")


def _draw_page_chrome(c: pdfcanvas.Canvas, doc: SimpleDocTemplate) -> None:
    if _HEADER_BAND.is_file():
        c.drawImage(
            str(_HEADER_BAND),
            0,
            _PAGE_H - _HEADER_H,
            width=_PAGE_W,
            height=_HEADER_H,
            preserveAspectRatio=False,
            mask="auto",
        )
    else:
        logger.warning("PDF header band missing at %s", _HEADER_BAND)
        c.setFillColor(_NAVY)
        c.rect(0, _PAGE_H - _HEADER_H, _PAGE_W, _HEADER_H, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(_SIDE, _PAGE_H - 55, "Clínica Monte Grande · Canning Health Institute")

    c.setFillColor(_TITLE_BG)
    c.rect(0, _PAGE_H - _CONTENT_TOP, _PAGE_W, _TITLE_BAND_H, fill=1, stroke=0)
    c.setFillColor(_TITLE_FG)
    c.setFont("Helvetica", 28)
    c.drawString(_SIDE, _PAGE_H - _HEADER_H - 48, _DOC_TITLE)

    c.setStrokeColor(_LINE)
    c.setLineWidth(0.4)
    c.line(_SIDE * 0.5, _FOOTER_Y + 14, _PAGE_W - _SIDE * 0.5, _FOOTER_Y + 14)
    c.setFillColor(_NAVY)
    c.setFont("Helvetica", 6)
    c.drawString(23, _FOOTER_Y, _FOOTER_LABEL)
    c.drawRightString(_PAGE_W - 23, _FOOTER_Y, f"{doc.page:02d}")


def _section_heading(text: str, styles: Any, content_width: float) -> Table:
    bar_w = 1.4
    gap = 8.0
    bar = Table([[""]], colWidths=[bar_w], rowHeights=[18])
    bar.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), _NAVY),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    heading = Paragraph(text.upper(), styles["section"])
    text_w = max(content_width - bar_w - gap, 40)
    wrap = Table([[bar, heading]], colWidths=[bar_w + gap, text_w])
    wrap.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (0, 0), 0),
                ("RIGHTPADDING", (0, 0), (0, 0), gap),
                ("LEFTPADDING", (1, 0), (1, 0), 0),
                ("RIGHTPADDING", (1, 0), (1, 0), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return wrap


def _styles() -> Any:
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="section",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=_NAVY,
        )
    )
    styles.add(
        ParagraphStyle(
            name="body",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=11,
            textColor=_BODY_FG,
            alignment=TA_LEFT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="body_right",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=11,
            textColor=_BODY_FG,
            alignment=TA_RIGHT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="th",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=_TITLE_FG,
            alignment=TA_LEFT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="muted",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            textColor=_MUTED,
            leading=13,
        )
    )
    styles.add(
        ParagraphStyle(
            name="name",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=14,
            textColor=_BODY_FG,
            spaceAfter=2,
        )
    )
    return styles


def _prof_block(
    row: ValoresExtrasProfesionalRow,
    styles: Any,
    usable: float,
    periodo_label: str,
) -> list[Any]:
    parts: list[Any] = []
    parts.append(_section_heading("Profesional", styles, usable))
    parts.append(Spacer(1, 3 * mm))
    parts.append(Paragraph(f"<b>{row.professional_name}</b>", styles["name"]))
    legajo = row.legajo or "—"
    parts.append(Paragraph(f"Legajo {legajo}", styles["muted"]))
    parts.append(Paragraph(f"Período: {periodo_label}", styles["muted"]))
    parts.append(
        Paragraph(
            f"Módulos: {row.cant_modulos} ({_money(row.importe_modulos)}) · "
            f"Novedades: {row.cant_novedades} ({_money(row.importe_novedades)}) · "
            f"Total: {_money(row.importe_total)}",
            styles["muted"],
        )
    )
    parts.append(Spacer(1, 5 * mm))
    parts.append(_section_heading("Detalle", styles, usable))
    parts.append(Spacer(1, 3 * mm))

    # Compact columns for A4 portrait
    headers = [
        Paragraph("Fecha", styles["th"]),
        Paragraph("Tipo", styles["th"]),
        Paragraph("Concepto", styles["th"]),
        Paragraph("Cant.", styles["th"]),
        Paragraph("Valor", styles["th"]),
        Paragraph("Importe", styles["th"]),
        Paragraph("Motivo / Obs.", styles["th"]),
        Paragraph("Servicio", styles["th"]),
    ]
    col_w = [
        usable * 0.10,
        usable * 0.08,
        usable * 0.18,
        usable * 0.07,
        usable * 0.10,
        usable * 0.11,
        usable * 0.20,
        usable * 0.16,
    ]
    data: list[list[Any]] = [headers]
    if not row.detalle:
        data.append(
            [
                Paragraph("Sin cargas", styles["muted"]),
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ]
        )
    else:
        for d in row.detalle:
            fecha = d.fecha_realizacion.isoformat() if d.fecha_realizacion else "—"
            obs_bits = []
            if d.motivo_label:
                obs_bits.append(d.motivo_label)
            if d.observaciones:
                obs_bits.extend(d.observaciones)
            obs = " · ".join(obs_bits) if obs_bits else "—"
            data.append(
                [
                    Paragraph(fecha, styles["body"]),
                    Paragraph(d.tipo or "—", styles["body"]),
                    Paragraph(d.concepto or "—", styles["body"]),
                    Paragraph(_qty(d.cantidad_horas), styles["body_right"]),
                    Paragraph(_money(d.valor_unitario) if d.valor_unitario is not None else "—", styles["body_right"]),
                    Paragraph(_money(d.importe), styles["body_right"]),
                    Paragraph(obs, styles["body"]),
                    Paragraph(d.servicio_nombre or "—", styles["body"]),
                ]
            )

    table = Table(data, colWidths=col_w, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), _TITLE_BG),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LINEBELOW", (0, 0), (-1, -1), 0.4, _LINE),
                ("BOX", (0, 0), (-1, -1), 0.4, _LINE),
            ]
        )
    )
    parts.append(table)
    return [KeepTogether(parts)] if len(row.detalle) <= 8 else parts


def build_valores_extras_pdf(
    *,
    data: ValoresExtrasResponse,
    periodo_nombre: str | None,
) -> tuple[bytes, str]:
    periodo_label = periodo_nombre or f"#{data.periodo_id}"
    filename = build_filename(periodo_nombre=periodo_nombre, periodo_id=data.periodo_id)

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=_SIDE,
        rightMargin=_SIDE,
        topMargin=_CONTENT_TOP + 16,
        bottomMargin=_FOOTER_Y + 22,
        title=_DOC_TITLE,
    )
    styles = _styles()
    usable = _PAGE_W - doc.leftMargin - doc.rightMargin
    story: list[Any] = []

    for idx, prof in enumerate(data.profesionales):
        if idx > 0:
            story.append(PageBreak())
        story.extend(_prof_block(prof, styles, usable, periodo_label))

    if not data.profesionales:
        story.append(_section_heading("Profesional", styles, usable))
        story.append(Spacer(1, 3 * mm))
        story.append(Paragraph("Sin profesionales seleccionados.", styles["muted"]))

    doc.build(story, onFirstPage=_draw_page_chrome, onLaterPages=_draw_page_chrome)
    return buf.getvalue(), filename
