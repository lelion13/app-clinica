from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_operator_or_admin
from app.db.session import get_db
from app.models.consulting_room import ConsultingRoom
from app.models.professional import Professional
from app.models.user import User
from app.models.weekly_assignment import RoomWeeklyAssignment
from app.schemas.weekly_assignment import WeeklyAssignmentCreateRequest, WeeklyAssignmentResponse
from app.services.weekly_assignment_service import (
    create_weekly_assignment,
    delete_weekly_assignment,
    list_weekly_assignments,
)

router = APIRouter()


def _to_response(db: Session, item: RoomWeeklyAssignment) -> WeeklyAssignmentResponse:
    room = db.execute(
        select(ConsultingRoom).where(ConsultingRoom.id == item.room_id, ConsultingRoom.deleted_at.is_(None))
    ).scalar_one()
    professional = db.execute(
        select(Professional).where(Professional.id == item.professional_id, Professional.deleted_at.is_(None))
    ).scalar_one()
    return WeeklyAssignmentResponse(
        id=item.id,
        room_id=item.room_id,
        room_code=room.code,
        location_id=room.location_id,
        professional_id=item.professional_id,
        professional_full_name=professional.full_name,
        weekday=item.weekday,
        start_time=item.start_time,
        end_time=item.end_time,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get("", response_model=list[WeeklyAssignmentResponse])
def weekly_assignments_list(
    location_id: int | None = Query(default=None),
    room_id: int | None = Query(default=None),
    professional_id: int | None = Query(default=None),
    weekday: int | None = Query(default=None, ge=0, le=6),
    db: Session = Depends(get_db),
    user: User = Depends(require_operator_or_admin),
) -> list[WeeklyAssignmentResponse]:
    _ = user
    rows = list_weekly_assignments(db, location_id, room_id, professional_id, weekday)
    return [_to_response(db, row) for row in rows]


@router.post("", response_model=WeeklyAssignmentResponse, status_code=status.HTTP_201_CREATED)
def weekly_assignments_create(
    payload: WeeklyAssignmentCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_operator_or_admin),
) -> WeeklyAssignmentResponse:
    item = create_weekly_assignment(db, payload, actor_id=user.id)
    return _to_response(db, item)


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def weekly_assignments_delete(
    assignment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_operator_or_admin),
) -> None:
    delete_weekly_assignment(db, assignment_id, actor_id=user.id)
