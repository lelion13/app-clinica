from datetime import datetime
from decimal import Decimal

import httpx
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.novedades import NovedadesProfesional
from app.schemas.novedades import NovedadesProfEspecialistaUnmatched, NovedadesProfSyncResponse

ESPECIALISTA_MODULO_FACTOR = Decimal("1.20")


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


def _normalize_especialista_row(raw: dict) -> tuple[str, str] | None:
    """Returns (codprof, descripcion) or None."""
    codprof = _as_str(raw.get("profesional") if "profesional" in raw else raw.get("CODPROF"))
    descripcion = _as_str(raw.get("descripcion") if "descripcion" in raw else raw.get("NOMBRES")) or ""
    if not codprof:
        return None
    return codprof[:40], (descripcion[:200] if descripcion else codprof)


def modulo_valor_para_profesional(catalog_valor: Decimal, *, es_especialista: bool) -> Decimal:
    base = Decimal(catalog_valor)
    if es_especialista:
        return (base * ESPECIALISTA_MODULO_FACTOR).quantize(Decimal("0.01"))
    return base


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


def _fetch_especialistas_rows() -> list[dict]:
    url = (settings.novedades_prof_especialistas_url or "").strip()
    token = (settings.novedades_prof_sync_token or "").strip()
    if not url:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="NOVEDADES_PROF_ESPECIALISTAS_URL no configurada",
        )
    if not token:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="NOVEDADES_PROF_SYNC_TOKEN no configurado",
        )
    timeout = settings.novedades_prof_especialistas_timeout or settings.novedades_prof_sync_timeout
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.get(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
            response.raise_for_status()
            payload = response.json()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error al consultar API de especialistas: {exc}",
        ) from exc

    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        for key in ("items", "data", "profesionales", "results", "especialistas"):
            inner = payload.get(key)
            if isinstance(inner, list):
                return [row for row in inner if isinstance(row, dict)]
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="Respuesta externa de especialistas con formato no reconocido",
    )


def apply_especialistas_flags(
    db: Session, *, actor_id: int, now: datetime | None = None
) -> tuple[int, list[NovedadesProfEspecialistaUnmatched], str | None]:
    """Set/clear es_especialista from remote list. Returns (matched, unmatched, warning)."""
    now = now or datetime.utcnow()
    try:
        remote_rows = _fetch_especialistas_rows()
    except HTTPException as exc:
        detail = exc.detail if isinstance(exc.detail, str) else "Error al consultar especialistas"
        return 0, [], detail

    remote_by_cod: dict[str, str] = {}
    for raw in remote_rows:
        normalized = _normalize_especialista_row(raw)
        if not normalized:
            continue
        codprof, descripcion = normalized
        remote_by_cod[codprof] = descripcion

    existing = list(
        db.execute(select(NovedadesProfesional).where(NovedadesProfesional.deleted_at.is_(None))).scalars().all()
    )
    by_cod = {row.codprof: row for row in existing}
    matched = 0
    for row in existing:
        want = row.codprof in remote_by_cod
        if row.es_especialista != want:
            row.es_especialista = want
            row.updated_at = now
            row.updated_by = actor_id
        if want:
            matched += 1

    unmatched = [
        NovedadesProfEspecialistaUnmatched(profesional=cod, descripcion=desc)
        for cod, desc in sorted(remote_by_cod.items(), key=lambda x: x[0])
        if cod not in by_cod
    ]
    return matched, unmatched, None


def sync_novedades_professionals(
    db: Session, actor_id: int, *, sync_especialistas: bool = False
) -> NovedadesProfSyncResponse:
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
                es_especialista=False,
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

    especialistas_matched = 0
    unmatched: list[NovedadesProfEspecialistaUnmatched] = []
    especialistas_warning: str | None = None
    if sync_especialistas:
        especialistas_matched, unmatched, especialistas_warning = apply_especialistas_flags(
            db, actor_id=actor_id, now=now
        )
        if especialistas_warning is None:
            db.commit()

    return NovedadesProfSyncResponse(
        created=created,
        updated=updated,
        inactivated=inactivated,
        skipped=skipped,
        errors=errors[:50],
        synced_at=now,
        especialistas_matched=especialistas_matched,
        especialistas_unmatched=unmatched,
        especialistas_warning=especialistas_warning,
    )
