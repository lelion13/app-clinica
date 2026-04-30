from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_operator_or_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.consulting_room import (
    ConsultingRoomCreateRequest,
    ConsultingRoomResponse,
    ConsultingRoomUpdateRequest,
    RoomOperatingHourCreateRequest,
    RoomOperatingHourResponse,
    RoomOperatingHourUpdateRequest,
)
from app.services.consulting_room_service import (
    create_room,
    create_room_hour,
    delete_room,
    delete_room_hour,
    list_room_hours,
    list_rooms,
    update_room,
    update_room_hour,
)

router = APIRouter()


def _room_response(item) -> ConsultingRoomResponse:
    return ConsultingRoomResponse(
        id=item.id,
        location_id=item.location_id,
        code=item.code,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _hour_response(item) -> RoomOperatingHourResponse:
    return RoomOperatingHourResponse(
        id=item.id,
        room_id=item.room_id,
        weekday=item.weekday,
        start_time=item.start_time,
        end_time=item.end_time,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get("", response_model=list[ConsultingRoomResponse])
def rooms_list(db: Session = Depends(get_db), user: User = Depends(require_operator_or_admin)) -> list[ConsultingRoomResponse]:
    _ = user
    return [_room_response(item) for item in list_rooms(db)]


@router.post("", response_model=ConsultingRoomResponse, status_code=status.HTTP_201_CREATED)
def rooms_create(
    payload: ConsultingRoomCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_operator_or_admin),
) -> ConsultingRoomResponse:
    return _room_response(create_room(db, payload, actor_id=user.id))


@router.patch("/{room_id}", response_model=ConsultingRoomResponse)
def rooms_update(
    room_id: int,
    payload: ConsultingRoomUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_operator_or_admin),
) -> ConsultingRoomResponse:
    return _room_response(update_room(db, room_id, payload, actor_id=user.id))


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def rooms_delete(room_id: int, db: Session = Depends(get_db), user: User = Depends(require_operator_or_admin)) -> None:
    delete_room(db, room_id, actor_id=user.id)


@router.get("/{room_id}/hours", response_model=list[RoomOperatingHourResponse])
def room_hours_list(
    room_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_operator_or_admin),
) -> list[RoomOperatingHourResponse]:
    _ = user
    return [_hour_response(item) for item in list_room_hours(db, room_id)]


@router.post("/hours", response_model=RoomOperatingHourResponse, status_code=status.HTTP_201_CREATED)
def room_hours_create(
    payload: RoomOperatingHourCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_operator_or_admin),
) -> RoomOperatingHourResponse:
    return _hour_response(create_room_hour(db, payload, actor_id=user.id))


@router.patch("/hours/{hour_id}", response_model=RoomOperatingHourResponse)
def room_hours_update(
    hour_id: int,
    payload: RoomOperatingHourUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_operator_or_admin),
) -> RoomOperatingHourResponse:
    return _hour_response(update_room_hour(db, hour_id, payload, actor_id=user.id))


@router.delete("/hours/{hour_id}", status_code=status.HTTP_204_NO_CONTENT)
def room_hours_delete(
    hour_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_operator_or_admin),
) -> None:
    delete_room_hour(db, hour_id, actor_id=user.id)
