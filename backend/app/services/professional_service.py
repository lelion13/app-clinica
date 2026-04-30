from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.professional import Professional
from app.schemas.professional import ProfessionalCreateRequest, ProfessionalUpdateRequest


def list_professionals(db: Session) -> list[Professional]:
    return list(
        db.execute(select(Professional).where(Professional.deleted_at.is_(None)).order_by(Professional.id)).scalars().all()
    )


def create_professional(db: Session, payload: ProfessionalCreateRequest, actor_id: int) -> Professional:
    if payload.license_number:
        existing = db.execute(
            select(Professional).where(
                Professional.license_number == payload.license_number.strip(),
                Professional.deleted_at.is_(None),
            )
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La matricula ya existe")
    now = datetime.utcnow()
    item = Professional(
        full_name=payload.full_name.strip(),
        license_number=payload.license_number.strip() if payload.license_number else None,
        created_at=now,
        updated_at=now,
        created_by=actor_id,
        updated_by=actor_id,
        deleted_at=None,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_professional(db: Session, professional_id: int, payload: ProfessionalUpdateRequest, actor_id: int) -> Professional:
    item = db.execute(
        select(Professional).where(Professional.id == professional_id, Professional.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profesional no encontrado")

    if payload.full_name is not None:
        item.full_name = payload.full_name.strip()
    if payload.license_number is not None:
        item.license_number = payload.license_number.strip() or None
    item.updated_at = datetime.utcnow()
    item.updated_by = actor_id
    db.commit()
    db.refresh(item)
    return item


def delete_professional(db: Session, professional_id: int, actor_id: int) -> None:
    item = db.execute(
        select(Professional).where(Professional.id == professional_id, Professional.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profesional no encontrado")
    item.deleted_at = datetime.utcnow()
    item.updated_at = datetime.utcnow()
    item.updated_by = actor_id
    db.commit()
