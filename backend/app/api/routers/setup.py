from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.setup import BootstrapAdminRequest
from app.services.setup_service import bootstrap_admin

router = APIRouter()


@router.post("/bootstrap-admin", status_code=status.HTTP_201_CREATED)
def setup_bootstrap_admin(payload: BootstrapAdminRequest, db: Session = Depends(get_db)) -> dict:
    user = bootstrap_admin(db, payload.name, payload.email, payload.password)
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role.value,
    }
