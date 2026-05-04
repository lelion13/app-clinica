from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_operator_or_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.professional import ProfessionalResponse, ProfessionalSyncResponse
from app.services.professional_service import (
    list_professionals,
    sync_professionals_from_external,
)

router = APIRouter()


def _to_response(item) -> ProfessionalResponse:
    return ProfessionalResponse(
        id=item.id,
        full_name=item.full_name,
        license_number=item.license_number,
        external_document=item.external_document,
        email=item.email,
        profession=item.profession,
        license_type=item.license_type,
        specialty=item.specialty,
        external_status=item.external_status,
        is_active=item.is_active,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get("", response_model=list[ProfessionalResponse])
def professionals_list(
    include_inactive: bool = Query(default=False),
    db: Session = Depends(get_db),
    user: User = Depends(require_operator_or_admin),
) -> list[ProfessionalResponse]:
    _ = user
    return [_to_response(item) for item in list_professionals(db, include_inactive=include_inactive)]


@router.post("/sync", response_model=ProfessionalSyncResponse, status_code=status.HTTP_200_OK)
def professionals_sync(
    db: Session = Depends(get_db),
    user: User = Depends(require_operator_or_admin),
) -> ProfessionalSyncResponse:
    return sync_professionals_from_external(db, actor_id=user.id)
