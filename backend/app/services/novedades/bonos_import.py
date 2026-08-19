from collections import defaultdict
from datetime import datetime

import httpx
from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.novedades import (
    NovedadesBonoCantidad,
    NovedadesBonoOpcion,
    NovedadesPeriodo,
    NovedadesProfesional,
    PeriodoEstado,
)
from app.models.user import User
from app.schemas.novedades import (
    BonoColumnaResponse,
    BonosImportResponse,
    SoloBonoRowResponse,
)


def opcion_key(centro: str, servicio: str, semana: str, horario: str) -> str:
    return f"{centro}|{servicio}|{semana}|{horario}"


def opcion_label(centro: str, servicio: str, semana: str, horario: str) -> str:
    return f"{centro} · {servicio} · {semana} · {horario}"


def _as_str(value) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    return s or None


def _as_int(value) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _normalize_remote_item(raw: dict) -> tuple[str, str, str, str, str, int] | None:
    centro = _as_str(raw.get("centro"))
    servicio = _as_str(raw.get("servicio"))
    semana = _as_str(raw.get("semana"))
    horario = _as_str(raw.get("horario"))
    profesional = _as_str(raw.get("profesional"))
    cantidad = _as_int(raw.get("cantidad"))
    if not all([centro, servicio, semana, horario, profesional]) or cantidad is None:
        return None
    return (
        centro[:80],
        servicio[:80],
        semana[:80],
        horario[:80],
        profesional[:40],
        cantidad,
    )


def _fetch_remote_bonos(fecha_desde: str, fecha_hasta: str) -> list[dict]:
    url = (settings.novedades_bonos_resumen_url or "").strip()
    token = (settings.novedades_prof_sync_token or "").strip()
    if not url or not token:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Importación de bonos no configurada (NOVEDADES_BONOS_RESUMEN_URL / NOVEDADES_PROF_SYNC_TOKEN)",
        )
    try:
        with httpx.Client(timeout=settings.novedades_bonos_resumen_timeout) as client:
            response = client.get(
                url,
                params={"fecha_desde": fecha_desde, "fecha_hasta": fecha_hasta},
                headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            )
            response.raise_for_status()
            payload = response.json()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error al consultar API de bonos: {exc}",
        ) from exc

    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        for key in ("items", "data", "results", "bonos"):
            inner = payload.get(key)
            if isinstance(inner, list):
                return [row for row in inner if isinstance(row, dict)]
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="Respuesta externa de bonos con formato no reconocido",
    )


def _get_or_create_opcion(
    db: Session,
    *,
    centro: str,
    servicio: str,
    semana: str,
    horario: str,
    actor_id: int,
    now: datetime,
    cache: dict[tuple[str, str, str, str], NovedadesBonoOpcion],
) -> NovedadesBonoOpcion:
    key = (centro, servicio, semana, horario)
    cached = cache.get(key)
    if cached:
        return cached
    existing = db.execute(
        select(NovedadesBonoOpcion).where(
            NovedadesBonoOpcion.centro == centro,
            NovedadesBonoOpcion.servicio == servicio,
            NovedadesBonoOpcion.semana == semana,
            NovedadesBonoOpcion.horario == horario,
            NovedadesBonoOpcion.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if existing:
        cache[key] = existing
        return existing
    item = NovedadesBonoOpcion(
        centro=centro,
        servicio=servicio,
        semana=semana,
        horario=horario,
        created_at=now,
        updated_at=now,
        created_by=actor_id,
        updated_by=actor_id,
        deleted_at=None,
    )
    db.add(item)
    db.flush()
    cache[key] = item
    return item


def import_bonos_for_periodo(db: Session, periodo_id: int, user: User) -> BonosImportResponse:
    periodo = db.execute(
        select(NovedadesPeriodo).where(NovedadesPeriodo.id == periodo_id, NovedadesPeriodo.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not periodo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Periodo no encontrado")
    if not periodo.fecha_inicio or not periodo.fecha_fin:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El período no tiene fecha_inicio/fecha_fin válidas",
        )
    if periodo.estado == PeriodoEstado.closed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El período está cerrado: no se puede reimportar bonos",
        )

    fecha_desde = periodo.fecha_inicio.isoformat()
    fecha_hasta = periodo.fecha_fin.isoformat()
    # Fetch BEFORE mutating snapshot (Q8).
    remote_rows = _fetch_remote_bonos(fecha_desde, fecha_hasta)

    professionals = {
        p.codprof: p
        for p in db.execute(select(NovedadesProfesional).where(NovedadesProfesional.deleted_at.is_(None)))
        .scalars()
        .all()
    }

    aggregated: dict[tuple[int, str, str, str, str], int] = defaultdict(int)
    received = 0
    ignored = 0
    for raw in remote_rows:
        normalized = _normalize_remote_item(raw)
        if not normalized:
            ignored += 1
            continue
        received += 1
        centro, servicio, semana, horario, codprof, cantidad = normalized
        prof = professionals.get(codprof)
        if not prof:
            ignored += 1
            continue
        aggregated[(prof.id, centro, servicio, semana, horario)] += cantidad

    now = datetime.utcnow()
    db.execute(delete(NovedadesBonoCantidad).where(NovedadesBonoCantidad.periodo_id == periodo_id))

    opcion_cache: dict[tuple[str, str, str, str], NovedadesBonoOpcion] = {}
    matched_prof_ids: set[int] = set()
    option_keys: set[str] = set()
    for (professional_id, centro, servicio, semana, horario), cantidad in aggregated.items():
        opcion = _get_or_create_opcion(
            db,
            centro=centro,
            servicio=servicio,
            semana=semana,
            horario=horario,
            actor_id=user.id,
            now=now,
            cache=opcion_cache,
        )
        db.add(
            NovedadesBonoCantidad(
                periodo_id=periodo_id,
                professional_id=professional_id,
                opcion_id=opcion.id,
                cantidad=cantidad,
                created_at=now,
                updated_at=now,
                created_by=user.id,
                updated_by=user.id,
                deleted_at=None,
            )
        )
        matched_prof_ids.add(professional_id)
        option_keys.add(opcion_key(centro, servicio, semana, horario))

    db.commit()

    from app.services.novedades.capital_humano import build_capital_humano_rows

    grid_rows = build_capital_humano_rows(db, periodo_id=periodo_id, include_bonos=True)
    grid_ids = {r.professional_id for r in grid_rows}
    solo_bonos = len(matched_prof_ids - grid_ids)

    return BonosImportResponse(
        received=received,
        matched=len(matched_prof_ids),
        solo_bonos=solo_bonos,
        columns=len(option_keys),
        ignored=ignored,
    )


def load_bonos_snapshot(
    db: Session, *, periodo_id: int | None
) -> tuple[list[BonoColumnaResponse], dict[int, dict[str, int]]]:
    if periodo_id is None:
        return [], {}

    rows = list(
        db.execute(
            select(NovedadesBonoCantidad, NovedadesBonoOpcion)
            .join(NovedadesBonoOpcion, NovedadesBonoOpcion.id == NovedadesBonoCantidad.opcion_id)
            .where(
                NovedadesBonoCantidad.periodo_id == periodo_id,
                NovedadesBonoCantidad.deleted_at.is_(None),
                NovedadesBonoOpcion.deleted_at.is_(None),
            )
        ).all()
    )
    columns_map: dict[str, BonoColumnaResponse] = {}
    by_prof: dict[int, dict[str, int]] = defaultdict(dict)
    for cantidad_row, opcion in rows:
        key = opcion_key(opcion.centro, opcion.servicio, opcion.semana, opcion.horario)
        if key not in columns_map:
            columns_map[key] = BonoColumnaResponse(
                key=key,
                label=opcion_label(opcion.centro, opcion.servicio, opcion.semana, opcion.horario),
                centro=opcion.centro,
                servicio=opcion.servicio,
                semana=opcion.semana,
                horario=opcion.horario,
            )
        by_prof[cantidad_row.professional_id][key] = int(cantidad_row.cantidad)

    columns = sorted(columns_map.values(), key=lambda c: c.label.lower())
    return columns, dict(by_prof)


def list_solo_bonos(
    db: Session,
    *,
    periodo_id: int,
    servicio_id: int | None = None,
) -> list[SoloBonoRowResponse]:
    columns, by_prof = load_bonos_snapshot(db, periodo_id=periodo_id)
    if not by_prof:
        return []
    _ = columns
    from app.services.novedades.capital_humano import build_capital_humano_rows

    grid_ids = {
        r.professional_id
        for r in build_capital_humano_rows(
            db, periodo_id=periodo_id, servicio_id=servicio_id, include_bonos=True
        )
    }
    solo_ids = [pid for pid in by_prof if pid not in grid_ids]
    if not solo_ids:
        return []

    professionals = {
        p.id: p
        for p in db.execute(
            select(NovedadesProfesional).where(
                NovedadesProfesional.id.in_(solo_ids),
                NovedadesProfesional.deleted_at.is_(None),
            )
        )
        .scalars()
        .all()
    }
    result: list[SoloBonoRowResponse] = []
    for pid in solo_ids:
        prof = professionals.get(pid)
        if not prof:
            continue
        bonos = by_prof.get(pid, {})
        result.append(
            SoloBonoRowResponse(
                professional_id=pid,
                codprof=prof.codprof,
                legajo=prof.legajo,
                professional_name=prof.full_name,
                bonos=bonos,
                total_cantidad=sum(bonos.values()),
            )
        )
    result.sort(key=lambda r: (r.professional_name or "").lower())
    return result
