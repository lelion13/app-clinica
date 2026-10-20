"""Proxy HTTP del resumen de turnos externo (Indicadores ocupación)."""

from __future__ import annotations

from datetime import date

import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.distribucion import TurnosResumenDetalleItem, TurnosResumenResponse


def _parse_date_param(raw: str, *, field: str) -> date:
    text = (raw or "").strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{field} es obligatorio (YYYY-MM-DD)",
        )
    try:
        return date.fromisoformat(text[:10])
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{field} con formato inválido (usar YYYY-MM-DD)",
        ) from exc


def _as_str(value) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    return s or None


def _rows_from_payload(payload: object) -> list[dict]:
    """Acepta array raíz o wrapper {detalle|items|data|results}."""
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        if "turno_horario_id" in payload:
            return [payload]
        for key in ("detalle", "items", "data", "results", "resumen"):
            inner = payload.get(key)
            if isinstance(inner, list):
                return [row for row in inner if isinstance(row, dict)]
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="Respuesta externa de resumen de turnos con formato no reconocido",
    )


def fetch_turnos_resumen(*, fecha_desde: str, fecha_hasta: str) -> TurnosResumenResponse:
    desde = _parse_date_param(fecha_desde, field="fecha_desde")
    hasta = _parse_date_param(fecha_hasta, field="fecha_hasta")
    if hasta < desde:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="fecha_hasta debe ser >= fecha_desde",
        )

    url = (settings.distribucion_turnos_resumen_url or "").strip()
    token = (settings.novedades_prof_sync_token or "").strip()
    if not url or not token:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Resumen de turnos no configurado (DISTRIBUCION_TURNOS_RESUMEN_URL / NOVEDADES_PROF_SYNC_TOKEN)",
        )

    try:
        with httpx.Client(timeout=settings.distribucion_turnos_resumen_timeout) as client:
            response = client.get(
                url,
                params={
                    "fecha_desde": desde.isoformat(),
                    "fecha_hasta": hasta.isoformat(),
                },
                headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            )
            response.raise_for_status()
            payload = response.json()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Error al consultar API externa de resumen de turnos",
        ) from exc

    raw_rows = _rows_from_payload(payload)
    detalle = [TurnosResumenDetalleItem.model_validate(row) for row in raw_rows]
    total = sum(float(item.total_turnos or 0) for item in detalle)

    meta_desde = None
    meta_hasta = None
    if isinstance(payload, dict):
        meta_desde = _as_str(payload.get("fecha_desde"))
        meta_hasta = _as_str(payload.get("fecha_hasta"))
        wrapped_total = payload.get("total_turnos")
        has_list = any(
            isinstance(payload.get(k), list) for k in ("detalle", "items", "data", "results", "resumen")
        )
        if wrapped_total is not None and has_list:
            try:
                total = float(wrapped_total)
            except (TypeError, ValueError):
                pass

    return TurnosResumenResponse(
        fecha_desde=meta_desde or desde.isoformat(),
        fecha_hasta=meta_hasta or hasta.isoformat(),
        total_turnos=total,
        detalle=detalle,
    )
