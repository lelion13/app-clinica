from datetime import datetime

import httpx
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.novedades import NovedadesProfesional
from app.schemas.novedades import NovedadesProfSyncResponse


def _as_str(value) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    return s or None


def _normalize_row(raw: dict) -> tuple[str, str, str | None, str | None] | None:
    """Returns (codprof, full_name, codprov, legajo) or None if unusable."""
    codprof = _as_str(raw.get("CODPROF") if "CODPROF" in raw else raw.get("codprof"))
    nombres = _as_str(raw.get("NOMBRES") if "NOMBRES" in raw else raw.get("nombres"))
    codprov = _as_str(raw.get("CODPROV") if "CODPROV" in raw else raw.get("codprov"))
    legajo = _as_str(raw.get("LEGAJO") if "LEGAJO" in raw else raw.get("legajo"))
    if not codprof or not nombres:
        return None
    return (
        codprof[:40],
        nombres[:200],
        (codprov[:40] if codprov else None),
        (legajo[:40] if legajo else None),
    )


def _fetch_remote_rows() -> list[dict]:
    url = (settings.novedades_prof_sync_url or "").strip()
    token = (settings.novedades_prof_sync_token or "").strip()
    if not url or not token:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Sync de profesionales Novedades no configurado (URL/TOKEN)",
        )
    try:
        with httpx.Client(timeout=settings.novedades_prof_sync_timeout) as client:
            response = client.get(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
            response.raise_for_status()
            payload = response.json()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error al consultar API externa de profesionales: {exc}",
        ) from exc

    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        for key in ("items", "data", "profesionales", "results"):
            inner = payload.get(key)
            if isinstance(inner, list):
                return [row for row in inner if isinstance(row, dict)]
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="Respuesta externa de profesionales con formato no reconocido",
    )


def sync_novedades_professionals(db: Session, actor_id: int) -> NovedadesProfSyncResponse:
    """Upsert by CODPROF; inactivate missing only after a successful fetch."""
    remote_rows = _fetch_remote_rows()
    now = datetime.utcnow()
    errors: list[str] = []
    created = updated = inactivated = skipped = 0
    seen: set[str] = set()

    existing = list(
        db.execute(select(NovedadesProfesional).where(NovedadesProfesional.deleted_at.is_(None))).scalars().all()
    )
    by_cod = {row.codprof: row for row in existing}

    for idx, raw in enumerate(remote_rows, start=1):
        normalized = _normalize_row(raw)
        if not normalized:
            skipped += 1
            errors.append(f"fila {idx}: CODPROF/NOMBRES faltantes")
            continue
        codprof, full_name, codprov, legajo = normalized
        if codprof in seen:
            skipped += 1
            errors.append(f"fila {idx}: CODPROF duplicado en respuesta ({codprof})")
            continue
        seen.add(codprof)

        row = by_cod.get(codprof)
        if row is None:
            row = NovedadesProfesional(
                codprof=codprof,
                full_name=full_name,
                codprov=codprov,
                legajo=legajo,
                is_active=True,
                created_at=now,
                updated_at=now,
                created_by=actor_id,
                updated_by=actor_id,
                deleted_at=None,
            )
            db.add(row)
            by_cod[codprof] = row
            created += 1
            continue

        changed = False
        if row.full_name != full_name:
            row.full_name = full_name
            changed = True
        if row.codprov != codprov:
            row.codprov = codprov
            changed = True
        if row.legajo != legajo:
            row.legajo = legajo
            changed = True
        if not row.is_active:
            row.is_active = True
            changed = True
        if changed:
            row.updated_at = now
            row.updated_by = actor_id
            updated += 1

    for codprof, row in by_cod.items():
        if codprof in seen:
            continue
        if row.is_active:
            row.is_active = False
            row.updated_at = now
            row.updated_by = actor_id
            inactivated += 1

    db.commit()
    return NovedadesProfSyncResponse(
        created=created,
        updated=updated,
        inactivated=inactivated,
        skipped=skipped,
        errors=errors[:50],
        synced_at=now,
    )
