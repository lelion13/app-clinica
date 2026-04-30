from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.location import Location
from app.schemas.location import LocationCreateRequest, LocationUpdateRequest


def list_locations(db: Session) -> list[Location]:
    return list(db.execute(select(Location).where(Location.deleted_at.is_(None)).order_by(Location.id)).scalars().all())


def create_location(db: Session, payload: LocationCreateRequest, actor_id: int) -> Location:
    existing = db.execute(
        select(Location).where(Location.name == payload.name.strip(), Location.deleted_at.is_(None))
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La ubicacion ya existe")
    now = datetime.utcnow()
    item = Location(
        name=payload.name.strip(),
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


def update_location(db: Session, location_id: int, payload: LocationUpdateRequest, actor_id: int) -> Location:
    item = db.execute(select(Location).where(Location.id == location_id, Location.deleted_at.is_(None))).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ubicacion no encontrada")
    item.name = payload.name.strip()
    item.updated_at = datetime.utcnow()
    item.updated_by = actor_id
    db.commit()
    db.refresh(item)
    return item


def delete_location(db: Session, location_id: int, actor_id: int) -> None:
    item = db.execute(select(Location).where(Location.id == location_id, Location.deleted_at.is_(None))).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ubicacion no encontrada")
    item.deleted_at = datetime.utcnow()
    item.updated_at = datetime.utcnow()
    item.updated_by = actor_id
    db.commit()
