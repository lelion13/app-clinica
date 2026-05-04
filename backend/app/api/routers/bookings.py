from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_operator_or_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.booking import (
    BookingCreateRequest,
    BookingRecurringCreateRequest,
    BookingResponse,
    BookingUpdateRequest,
)
from app.services.booking_service import create_booking, create_recurring_bookings, delete_booking, list_bookings, update_booking

router = APIRouter()


def _to_response(item) -> BookingResponse:
    return BookingResponse(
        id=item.id,
        room_id=item.room_id,
        professional_id=item.professional_id,
        start_at=item.start_at,
        end_at=item.end_at,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get("", response_model=list[BookingResponse])
def bookings_list(
    start_at: datetime | None = Query(default=None),
    end_at: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(require_operator_or_admin),
) -> list[BookingResponse]:
    _ = user
    return [_to_response(item) for item in list_bookings(db, start_at=start_at, end_at=end_at)]


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def bookings_create(
    payload: BookingCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_operator_or_admin),
) -> BookingResponse:
    return _to_response(create_booking(db, payload, actor_id=user.id))


@router.post("/recurring", response_model=list[BookingResponse], status_code=status.HTTP_201_CREATED)
def bookings_create_recurring(
    payload: BookingRecurringCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_operator_or_admin),
) -> list[BookingResponse]:
    created = create_recurring_bookings(db, payload, actor_id=user.id)
    return [_to_response(b) for b in created]


@router.patch("/{booking_id}", response_model=BookingResponse)
def bookings_update(
    booking_id: int,
    payload: BookingUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_operator_or_admin),
) -> BookingResponse:
    return _to_response(update_booking(db, booking_id, payload, actor_id=user.id))


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def bookings_delete(
    booking_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_operator_or_admin),
) -> None:
    delete_booking(db, booking_id, actor_id=user.id)
