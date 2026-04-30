from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.consulting_room import ConsultingRoom, RoomOperatingHour
from app.models.location import Location
from app.schemas.consulting_room import (
    ConsultingRoomCreateRequest,
    ConsultingRoomUpdateRequest,
    RoomOperatingHourCreateRequest,
    RoomOperatingHourUpdateRequest,
)


def list_rooms(db: Session) -> list[ConsultingRoom]:
    return list(
        db.execute(select(ConsultingRoom).where(ConsultingRoom.deleted_at.is_(None)).order_by(ConsultingRoom.id))
        .scalars()
        .all()
    )


def create_room(db: Session, payload: ConsultingRoomCreateRequest, actor_id: int) -> ConsultingRoom:
    location = db.execute(select(Location).where(Location.id == payload.location_id, Location.deleted_at.is_(None))).scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ubicacion no encontrada")
    existing = db.execute(
        select(ConsultingRoom).where(
            ConsultingRoom.location_id == payload.location_id,
            ConsultingRoom.code == payload.code.strip(),
            ConsultingRoom.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El consultorio ya existe en la ubicacion")
    now = datetime.utcnow()
    item = ConsultingRoom(
        location_id=payload.location_id,
        code=payload.code.strip(),
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


def update_room(db: Session, room_id: int, payload: ConsultingRoomUpdateRequest, actor_id: int) -> ConsultingRoom:
    item = db.execute(
        select(ConsultingRoom).where(ConsultingRoom.id == room_id, ConsultingRoom.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultorio no encontrado")
    if payload.location_id is not None:
        location = db.execute(
            select(Location).where(Location.id == payload.location_id, Location.deleted_at.is_(None))
        ).scalar_one_or_none()
        if not location:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ubicacion no encontrada")
        item.location_id = payload.location_id
    if payload.code is not None:
        item.code = payload.code.strip()
    item.updated_at = datetime.utcnow()
    item.updated_by = actor_id
    db.commit()
    db.refresh(item)
    return item


def delete_room(db: Session, room_id: int, actor_id: int) -> None:
    item = db.execute(
        select(ConsultingRoom).where(ConsultingRoom.id == room_id, ConsultingRoom.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultorio no encontrado")
    item.deleted_at = datetime.utcnow()
    item.updated_at = datetime.utcnow()
    item.updated_by = actor_id
    db.commit()


def list_room_hours(db: Session, room_id: int) -> list[RoomOperatingHour]:
    return list(
        db.execute(
            select(RoomOperatingHour)
            .where(RoomOperatingHour.room_id == room_id, RoomOperatingHour.deleted_at.is_(None))
            .order_by(RoomOperatingHour.weekday, RoomOperatingHour.start_time)
        )
        .scalars()
        .all()
    )


def create_room_hour(db: Session, payload: RoomOperatingHourCreateRequest, actor_id: int) -> RoomOperatingHour:
    if payload.start_time >= payload.end_time:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Rango horario invalido")
    room = db.execute(
        select(ConsultingRoom).where(ConsultingRoom.id == payload.room_id, ConsultingRoom.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultorio no encontrado")
    now = datetime.utcnow()
    item = RoomOperatingHour(
        room_id=payload.room_id,
        weekday=payload.weekday,
        start_time=payload.start_time,
        end_time=payload.end_time,
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


def update_room_hour(db: Session, hour_id: int, payload: RoomOperatingHourUpdateRequest, actor_id: int) -> RoomOperatingHour:
    item = db.execute(
        select(RoomOperatingHour).where(RoomOperatingHour.id == hour_id, RoomOperatingHour.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Horario operativo no encontrado")
    new_start = payload.start_time if payload.start_time is not None else item.start_time
    new_end = payload.end_time if payload.end_time is not None else item.end_time
    if new_start >= new_end:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Rango horario invalido")
    if payload.weekday is not None:
        item.weekday = payload.weekday
    if payload.start_time is not None:
        item.start_time = payload.start_time
    if payload.end_time is not None:
        item.end_time = payload.end_time
    item.updated_at = datetime.utcnow()
    item.updated_by = actor_id
    db.commit()
    db.refresh(item)
    return item


def delete_room_hour(db: Session, hour_id: int, actor_id: int) -> None:
    item = db.execute(
        select(RoomOperatingHour).where(RoomOperatingHour.id == hour_id, RoomOperatingHour.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Horario operativo no encontrado")
    item.deleted_at = datetime.utcnow()
    item.updated_at = datetime.utcnow()
    item.updated_by = actor_id
    db.commit()
