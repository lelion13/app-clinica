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
    NovedadesInternacionCantidad,
    NovedadesPeriodo,
    NovedadesPracticaCantidad,
    NovedadesProfesional,
    PeriodoEstado,
)
from app.models.user import User
from app.schemas.novedades import (
    BonoColumnaResponse,
    BonosImportResponse,
    SoloBonoRowResponse,
)

PRACTICA_KEY = "GLOBAL|PRACTICA_TRAUMATOLOGICA|—|—"
INTERNACION_KEY = "GLOBAL|INTERNACIONES|—|—"


def opcion_key(centro: str, servicio: str, semana: str, horario: str) -> str:
    return f"{centro}|{servicio}|{semana}|{horario}"


def opcion_label(centro: str, servicio: str, semana: str, horario: str) -> str:
    if centro == "GLOBAL" and servicio == "PRACTICA_TRAUMATOLOGICA":
        return "Práctica traumatológica"
    if centro == "GLOBAL" and servicio == "INTERNACIONES":
        return "Internaciones"
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


def _normalize_remote_practica(raw: dict) -> tuple[str, str, str, int] | None:
    centro = _as_str(raw.get("centro"))
    servicio = _as_str(raw.get("servicio"))
    profesional = _as_str(raw.get("profesional"))
    cantidad = _as_int(raw.get("cantidad"))
    if not all([centro, servicio, profesional]) or cantidad is None or cantidad <= 0:
        return None
    return (
        centro[:80],
        servicio[:80],
        profesional[:40],
        cantidad,
    )


def _fetch_remote_practicas(fecha_desde: str, fecha_hasta: str) -> list[dict]:
    url = (settings.novedades_bonos_practicas_url or "").strip()
    token = (settings.novedades_prof_sync_token or "").strip()
    if not url:
        return []
    if not token:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Token de sync no configurado para API de prácticas (NOVEDADES_PROF_SYNC_TOKEN)",
        )
    try:
        with httpx.Client(timeout=settings.novedades_bonos_practicas_timeout) as client:
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
            detail=f"Error al consultar API de prácticas: {exc}",
        ) from exc

    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        for key in ("items", "data", "results", "practicas"):
            inner = payload.get(key)
            if isinstance(inner, list):
                return [row for row in inner if isinstance(row, dict)]
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="Respuesta externa de prácticas con formato no reconocido",
    )


def _normalize_remote_internacion(raw: dict) -> tuple[str, str, int] | None:
    profesional = _as_str(raw.get("profesional"))
    sucursal = _as_str(raw.get("sucursal") or raw.get("centro"))
    cantidad = _as_int(raw.get("cantidad_internaciones") if "cantidad_internaciones" in raw else raw.get("cantidad"))
    if not all([profesional, sucursal]) or cantidad is None or cantidad <= 0:
        return None
    return (
        sucursal[:80],
        profesional[:40],
        cantidad,
    )


def _fetch_remote_internaciones(fecha_desde: str, fecha_hasta: str) -> list[dict]:
    url = (settings.novedades_bonos_internaciones_url or "").strip()
    token = (settings.novedades_prof_sync_token or "").strip()
    if not url:
        return []
    if not token:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Token de sync no configurado para API de internaciones (NOVEDADES_PROF_SYNC_TOKEN)",
        )
    try:
        with httpx.Client(timeout=settings.novedades_bonos_internaciones_timeout) as client:
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
            detail=f"Error al consultar API de internaciones: {exc}",
        ) from exc

    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        for key in ("items", "data", "results", "internaciones"):
            inner = payload.get(key)
            if isinstance(inner, list):
                return [row for row in inner if isinstance(row, dict)]
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="Respuesta externa de internaciones con formato no reconocido",
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


def cleanup_unused_opciones(
    db: Session,
    *,
    option_keys_from_import: set[str],
    actor_id: int,
    now: datetime,
) -> int:
    """Soft-delete opciones absent from import without tarifa and without cantidades anywhere."""
    from app.models.novedades import NovedadesProduccionTarifa

    tarifadas = set(
        db.execute(
            select(NovedadesProduccionTarifa.opcion_id).where(NovedadesProduccionTarifa.deleted_at.is_(None))
        )
        .scalars()
        .all()
    )
    with_cantidad = set(
        db.execute(
            select(NovedadesBonoCantidad.opcion_id).where(NovedadesBonoCantidad.deleted_at.is_(None)).distinct()
        )
        .scalars()
        .all()
    )
    opciones = list(
        db.execute(select(NovedadesBonoOpcion).where(NovedadesBonoOpcion.deleted_at.is_(None))).scalars().all()
    )
    removed = 0
    for opcion in opciones:
        if opcion.centro == "GLOBAL":
            continue
        key = opcion_key(opcion.centro, opcion.servicio, opcion.semana, opcion.horario)
        if key in option_keys_from_import:
            continue
        if opcion.id in tarifadas:
            continue
        if opcion.id in with_cantidad:
            continue
        opcion.deleted_at = now
        opcion.updated_at = now
        opcion.updated_by = actor_id
        removed += 1
    return removed


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
    # Fetch all remote APIs BEFORE mutating snapshot (atomic fail-closed).
    remote_rows = _fetch_remote_bonos(fecha_desde, fecha_hasta)
    remote_practicas = _fetch_remote_practicas(fecha_desde, fecha_hasta)
    remote_internaciones = _fetch_remote_internaciones(fecha_desde, fecha_hasta)

    professionals = {
        p.codprof: p
        for p in db.execute(select(NovedadesProfesional).where(NovedadesProfesional.deleted_at.is_(None)))
        .scalars()
        .all()
    }

    # 1. Bonos
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

    # 2. Prácticas
    practicas_aggregated: dict[tuple[int, str, str], int] = defaultdict(int)
    practicas_received = 0
    practicas_matched_profs: set[int] = set()
    for raw in remote_practicas:
        normalized_practica = _normalize_remote_practica(raw)
        if not normalized_practica:
            continue
        practicas_received += 1
        centro, servicio, codprof, cantidad = normalized_practica
        prof = professionals.get(codprof)
        if not prof:
            continue
        practicas_aggregated[(prof.id, centro, servicio)] += cantidad
        practicas_matched_profs.add(prof.id)

    # 3. Internaciones
    internaciones_aggregated: dict[tuple[int, str], int] = defaultdict(int)
    internaciones_received = 0
    internaciones_matched_profs: set[int] = set()
    for raw in remote_internaciones:
        normalized_internacion = _normalize_remote_internacion(raw)
        if not normalized_internacion:
            continue
        internaciones_received += 1
        sucursal, codprof, cantidad = normalized_internacion
        prof = professionals.get(codprof)
        if not prof:
            continue
        internaciones_aggregated[(prof.id, sucursal)] += cantidad
        internaciones_matched_profs.add(prof.id)

    now = datetime.utcnow()
    db.execute(delete(NovedadesBonoCantidad).where(NovedadesBonoCantidad.periodo_id == periodo_id))
    db.execute(delete(NovedadesPracticaCantidad).where(NovedadesPracticaCantidad.periodo_id == periodo_id))
    db.execute(delete(NovedadesInternacionCantidad).where(NovedadesInternacionCantidad.periodo_id == periodo_id))

    # Persist Bonos
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

    # Persist Prácticas
    for (professional_id, centro, servicio), cantidad in practicas_aggregated.items():
        db.add(
            NovedadesPracticaCantidad(
                periodo_id=periodo_id,
                professional_id=professional_id,
                centro=centro,
                servicio=servicio,
                cantidad=cantidad,
                created_at=now,
                updated_at=now,
                created_by=user.id,
                updated_by=user.id,
                deleted_at=None,
            )
        )

    # Persist Internaciones
    for (professional_id, sucursal), cantidad in internaciones_aggregated.items():
        db.add(
            NovedadesInternacionCantidad(
                periodo_id=periodo_id,
                professional_id=professional_id,
                sucursal=sucursal,
                cantidad=cantidad,
                created_at=now,
                updated_at=now,
                created_by=user.id,
                updated_by=user.id,
                deleted_at=None,
            )
        )

    from app.services.novedades.produccion_tarifas import ensure_special_produccion_opciones
    ensure_special_produccion_opciones(db, actor_id=user.id)

    cleanup_unused_opciones(db, option_keys_from_import=option_keys, actor_id=user.id, now=now)
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
        practicas_received=practicas_received,
        practicas_matched=len(practicas_matched_profs),
        internaciones_received=internaciones_received,
        internaciones_matched=len(internaciones_matched_profs),
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


def load_practicas_snapshot(
    db: Session, *, periodo_id: int | None
) -> dict[int, list[dict]]:
    if periodo_id is None:
        return {}
    rows = list(
        db.execute(
            select(NovedadesPracticaCantidad).where(
                NovedadesPracticaCantidad.periodo_id == periodo_id,
                NovedadesPracticaCantidad.deleted_at.is_(None),
            )
        ).scalars().all()
    )
    result: dict[int, list[dict]] = defaultdict(list)
    for row in rows:
        if hasattr(row, "professional_id"):
            result[row.professional_id].append({
                "centro": getattr(row, "centro", ""),
                "servicio": getattr(row, "servicio", ""),
                "cantidad": int(getattr(row, "cantidad", 0)),
            })
    return dict(result)


def load_internaciones_snapshot(
    db: Session, *, periodo_id: int | None
) -> dict[int, list[dict]]:
    if periodo_id is None:
        return {}
    rows = list(
        db.execute(
            select(NovedadesInternacionCantidad).where(
                NovedadesInternacionCantidad.periodo_id == periodo_id,
                NovedadesInternacionCantidad.deleted_at.is_(None),
            )
        ).scalars().all()
    )
    result: dict[int, list[dict]] = defaultdict(list)
    for row in rows:
        if hasattr(row, "professional_id"):
            result[row.professional_id].append({
                "sucursal": getattr(row, "sucursal", ""),
                "cantidad": int(getattr(row, "cantidad", 0)),
            })
    return dict(result)

