from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_operator_or_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.location import LocationCreateRequest, LocationResponse, LocationUpdateRequest
from app.services.location_service import create_location, delete_location, list_locations, update_location

router = APIRouter()


def _to_response(item) -> LocationResponse:
    return LocationResponse(id=item.id, name=item.name, created_at=item.created_at, updated_at=item.updated_at)


@router.get("", response_model=list[LocationResponse])
def locations_list(db: Session = Depends(get_db), user: User = Depends(require_operator_or_admin)) -> list[LocationResponse]:
    _ = user
    return [_to_response(item) for item in list_locations(db)]


@router.post("", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
def locations_create(
    payload: LocationCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_operator_or_admin),
) -> LocationResponse:
    return _to_response(create_location(db, payload, actor_id=user.id))


@router.put("/{location_id}", response_model=LocationResponse)
def locations_update(
    location_id: int,
    payload: LocationUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_operator_or_admin),
) -> LocationResponse:
    return _to_response(update_location(db, location_id, payload, actor_id=user.id))


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def locations_delete(
    location_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_operator_or_admin),
) -> None:
    delete_location(db, location_id, actor_id=user.id)
