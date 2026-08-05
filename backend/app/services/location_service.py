from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.location import Location
from app.schemas.location import LocationCreateRequest, LocationUpdateRequest


def list_locations(db: Session) -> list[Location]:
    return list(db.execute(select(Location).where(Location.deleted_at.is_(None)).order_by(Location.id)).scalars().all())


def _assert_unique_name(db: Session, name: str, *, exclude_id: int | None = None) -> None:
    query = select(Location).where(Location.name == name, Location.deleted_at.is_(None))
    if exclude_id is not None:
        query = query.where(Location.id != exclude_id)
    if db.execute(query).scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La ubicacion ya existe")


def _assert_unique_dominio_tipo(
    db: Session, id_dominio: int, tipo: str, *, exclude_id: int | None = None
) -> None:
    query = select(Location).where(
        Location.id_dominio == id_dominio,
        Location.tipo == tipo,
        Location.deleted_at.is_(None),
    )
    if exclude_id is not None:
        query = query.where(Location.id != exclude_id)
    if db.execute(query).scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una ubicacion con ese id_dominio y tipo",
        )


def create_location(db: Session, payload: LocationCreateRequest, actor_id: int) -> Location:
    name = payload.name.strip()
    tipo = payload.tipo.strip()
    _assert_unique_name(db, name)
    _assert_unique_dominio_tipo(db, payload.id_dominio, tipo)
    now = datetime.utcnow()
    item = Location(
        name=name,
        id_dominio=payload.id_dominio,
        tipo=tipo,
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
    name = payload.name.strip()
    tipo = payload.tipo.strip()
    _assert_unique_name(db, name, exclude_id=location_id)
    _assert_unique_dominio_tipo(db, payload.id_dominio, tipo, exclude_id=location_id)
    item.name = name
    item.id_dominio = payload.id_dominio
    item.tipo = tipo
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
