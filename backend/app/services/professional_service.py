from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import create_engine, select, text
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


def _external_mysql_url() -> str:
    if not settings.ext_db_host or not settings.ext_db_name or not settings.ext_db_user:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Configuración externa incompleta (EXT_DB_HOST/NAME/USER)",
        )
    return (
        f"mysql+pymysql://{settings.ext_db_user}:{settings.ext_db_password}"
        f"@{settings.ext_db_host}:{settings.ext_db_port}/{settings.ext_db_name}"
        f"?charset={settings.ext_db_charset}"
    )


def sync_professionals_from_external(db: Session, actor_id: int) -> ProfessionalSyncResponse:
    if not settings.ext_db_enabled:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Sincronización externa deshabilitada")

    ext_engine = create_engine(
        _external_mysql_url(),
        pool_pre_ping=True,
        connect_args={"connect_timeout": settings.ext_db_connect_timeout},
    )
    errors: list[str] = []
    now = datetime.utcnow()

    try:
        with ext_engine.connect() as conn:
            rows = conn.execute(text(settings.prof_sync_query)).mappings().all()
    except Exception as exc:  # pragma: no cover - external connectivity
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Error consultando base externa: {exc}") from exc
    finally:
        ext_engine.dispose()

    existing = list(db.execute(select(Professional).where(Professional.deleted_at.is_(None))).scalars().all())
    by_doc = {str(p.external_document): p for p in existing if p.external_document}

    seen_docs: set[str] = set()
    created = 0
    updated = 0
    skipped = 0

    for idx, row in enumerate(rows, start=1):
        doc = str((row.get("numero_documento") or "")).strip()
        if not doc:
            skipped += 1
            errors.append(f"Fila {idx}: numero_documento vacío")
            continue

        seen_docs.add(doc)
        full_name = str((row.get("nombres") or "")).strip()
        if not full_name:
            skipped += 1
            errors.append(f"Documento {doc}: nombres vacío")
            continue

        external_status = str((row.get("estado_usuario") or "")).strip()
        is_active = external_status == "A"
        license_number = str((row.get("numero_matricula") or "")).strip() or None
        item = by_doc.get(doc)

        if item is None:
            item = Professional(
                external_document=doc,
                full_name=full_name,
                email=str((row.get("email") or "")).strip() or None,
                profession=str((row.get("profesion") or "")).strip() or None,
                license_type=str((row.get("tipo_matricula") or "")).strip() or None,
                license_number=license_number,
                specialty=str((row.get("especialidad") or "")).strip() or None,
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
        item.email = str((row.get("email") or "")).strip() or None
        item.profession = str((row.get("profesion") or "")).strip() or None
        item.license_type = str((row.get("tipo_matricula") or "")).strip() or None
        item.license_number = license_number
        item.specialty = str((row.get("especialidad") or "")).strip() or None
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

    db.commit()
    return ProfessionalSyncResponse(
        created=created,
        updated=updated,
        inactivated=inactivated,
        skipped=skipped,
        errors=errors[:100],
        synced_at=now,
    )
