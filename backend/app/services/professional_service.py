from datetime import datetime
from urllib.parse import quote_plus

from fastapi import HTTPException, status
from sqlalchemy import create_engine, select, text
from sqlalchemy.exc import IntegrityError, ProgrammingError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.professional import Professional
from app.schemas.professional import ProfessionalSyncResponse


def list_professionals(db: Session, include_inactive: bool = False) -> list[Professional]:
    query = select(Professional).where(Professional.deleted_at.is_(None))
    if not include_inactive:
        query = query.where(Professional.is_active.is_(True))
    query = query.order_by(Professional.full_name, Professional.id)
    return list(db.execute(query).scalars().all())


def _truncate(value: str | None, max_len: int) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    return s[:max_len]


def _external_mysql_url() -> str:
    if not settings.ext_db_host or not settings.ext_db_name or not settings.ext_db_user:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Configuración externa incompleta (EXT_DB_HOST/NAME/USER)",
        )
    user = quote_plus(settings.ext_db_user)
    password = quote_plus(settings.ext_db_password)
    db_name = quote_plus(settings.ext_db_name)
    return f"mysql+pymysql://{user}:{password}@{settings.ext_db_host}:{settings.ext_db_port}/{db_name}?charset={settings.ext_db_charset}"


def _mysql_connect_args() -> dict:
    args: dict = {"connect_timeout": settings.ext_db_connect_timeout}
    if settings.ext_db_ssl_disabled:
        args["ssl_disabled"] = True
    return args


def _resolve_license_number(
    db: Session,
    external_document: str,
    raw_license: str | None,
    taken_licenses: set[str],
    current_license: str | None = None,
) -> str | None:
    """Evita violar uq_prof_license (DB + filas nuevas en esta corrida)."""
    lic = _truncate(raw_license, 80)
    if not lic:
        return None
    other = db.execute(
        select(Professional).where(
            Professional.deleted_at.is_(None),
            Professional.license_number == lic,
            Professional.external_document != external_document,
        )
    ).scalar_one_or_none()
    candidate = lic
    if other:
        suffix = f" ({external_document})"
        candidate = (lic[: max(0, 80 - len(suffix))] + suffix)[:80]
    if candidate in taken_licenses and candidate != current_license:
        candidate = f"{lic}|{external_document}"[:80]
        n = 2
        while candidate in taken_licenses and candidate != current_license and n < 50:
            candidate = f"{lic}|{external_document}|{n}"[:80]
            n += 1
    taken_licenses.add(candidate)
    return candidate


def sync_professionals_from_external(db: Session, actor_id: int) -> ProfessionalSyncResponse:
    if not settings.ext_db_enabled:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Sincronización externa deshabilitada")

    try:
        ext_engine = create_engine(
            _external_mysql_url(),
            pool_pre_ping=True,
            connect_args=_mysql_connect_args(),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"No se pudo inicializar conexión externa MySQL (driver/config): {exc}",
        ) from exc

    errors: list[str] = []
    now = datetime.utcnow()

    try:
        with ext_engine.connect() as conn:
            rows = conn.execute(text(settings.prof_sync_query)).mappings().all()
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Error consultando base externa: {exc}") from exc
    finally:
        ext_engine.dispose()

    existing = list(db.execute(select(Professional).where(Professional.deleted_at.is_(None))).scalars().all())
    by_doc = {str(p.external_document): p for p in existing if p.external_document}

    seen_docs: set[str] = set()
    taken_licenses: set[str] = set()

    created = 0
    updated = 0
    skipped = 0

    for idx, row in enumerate(rows, start=1):
        doc = _truncate(str(row.get("numero_documento") or ""), 40)
        if not doc:
            skipped += 1
            errors.append(f"Fila {idx}: numero_documento vacío")
            continue

        seen_docs.add(doc)
        full_name = _truncate(str(row.get("nombres") or ""), 120)
        if not full_name:
            skipped += 1
            errors.append(f"Documento {doc}: nombres vacío")
            continue

        external_status = _truncate(str(row.get("estado_usuario") or ""), 8) or ""
        is_active = external_status == "A"
        raw_matricula = str(row.get("numero_matricula") or "").strip() or None
        item = by_doc.get(doc)
        license_number = _resolve_license_number(
            db, doc, raw_matricula, taken_licenses, item.license_number if item else None
        )

        if item is None:
            item = Professional(
                external_document=doc,
                full_name=full_name,
                email=_truncate(str(row.get("email") or ""), 255),
                profession=_truncate(str(row.get("profesion") or ""), 80),
                license_type=_truncate(str(row.get("tipo_matricula") or ""), 80),
                license_number=license_number,
                specialty=_truncate(str(row.get("especialidad") or ""), 500),
                external_status=external_status or None,
                is_active=is_active,
                created_at=now,
                updated_at=now,
                created_by=actor_id,
                updated_by=actor_id,
                deleted_at=None,
            )
            db.add(item)
            by_doc[doc] = item
            created += 1
            continue

        item.full_name = full_name
        item.email = _truncate(str(row.get("email") or ""), 255)
        item.profession = _truncate(str(row.get("profesion") or ""), 80)
        item.license_type = _truncate(str(row.get("tipo_matricula") or ""), 80)
        item.license_number = license_number
        item.specialty = _truncate(str(row.get("especialidad") or ""), 500)
        item.external_status = external_status or None
        item.is_active = is_active
        item.updated_at = now
        item.updated_by = actor_id
        updated += 1

    inactivated = 0
    for p in existing:
        if p.external_document and p.external_document not in seen_docs and p.is_active:
            p.is_active = False
            p.external_status = "I"
            p.updated_at = now
            p.updated_by = actor_id
            inactivated += 1

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Conflicto al guardar profesionales (matrícula o documento duplicado): {exc}",
        ) from exc
    except ProgrammingError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Esquema local desactualizado. Ejecutá en el servidor: alembic upgrade head. Detalle: {exc}",
        ) from exc

    return ProfessionalSyncResponse(
        created=created,
        updated=updated,
        inactivated=inactivated,
        skipped=skipped,
        errors=errors[:100],
        synced_at=now,
    )
