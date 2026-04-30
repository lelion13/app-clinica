from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_operator_or_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.professional import ProfessionalCreateRequest, ProfessionalResponse, ProfessionalUpdateRequest
from app.services.professional_service import (
    create_professional,
    delete_professional,
    list_professionals,
    update_professional,
)

router = APIRouter()


def _to_response(item) -> ProfessionalResponse:
    return ProfessionalResponse(
        id=item.id,
        full_name=item.full_name,
        license_number=item.license_number,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get("", response_model=list[ProfessionalResponse])
def professionals_list(
    db: Session = Depends(get_db),
    user: User = Depends(require_operator_or_admin),
) -> list[ProfessionalResponse]:
    _ = user
    return [_to_response(item) for item in list_professionals(db)]


@router.post("", response_model=ProfessionalResponse, status_code=status.HTTP_201_CREATED)
def professionals_create(
    payload: ProfessionalCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_operator_or_admin),
) -> ProfessionalResponse:
    return _to_response(create_professional(db, payload, actor_id=user.id))


@router.patch("/{professional_id}", response_model=ProfessionalResponse)
def professionals_update(
    professional_id: int,
    payload: ProfessionalUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_operator_or_admin),
) -> ProfessionalResponse:
    return _to_response(update_professional(db, professional_id, payload, actor_id=user.id))


@router.delete("/{professional_id}", status_code=status.HTTP_204_NO_CONTENT)
def professionals_delete(
    professional_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_operator_or_admin),
) -> None:
    delete_professional(db, professional_id, actor_id=user.id)
