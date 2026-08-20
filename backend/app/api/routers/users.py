from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreateRequest,
    UserCreateResponse,
    UserResponse,
    UserUpdateRequest,
    WelcomeEmailResponse,
)
from app.services.user_service import create_user, delete_user, list_users, resend_welcome_email, update_user

router = APIRouter()


def _to_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role.value,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.get("", response_model=list[UserResponse])
def users_list(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> list[UserResponse]:
    _ = admin
    users = list_users(db)
    return [_to_response(item) for item in users]


@router.post("", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
def users_create(
    payload: UserCreateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> UserCreateResponse:
    user, welcome_sent, warning = create_user(db, payload, actor_id=admin.id)
    base = _to_response(user)
    return UserCreateResponse(
        **base.model_dump(),
        welcome_email_sent=welcome_sent,
        welcome_email_warning=warning,
    )


@router.patch("/{user_id}", response_model=UserResponse)
def users_update(
    user_id: int,
    payload: UserUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> UserResponse:
    user = update_user(db, user_id, payload, actor_id=admin.id)
    return _to_response(user)


@router.post("/{user_id}/resend-welcome", response_model=WelcomeEmailResponse)
def users_resend_welcome(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> WelcomeEmailResponse:
    _ = admin
    sent, warning = resend_welcome_email(db, user_id)
    return WelcomeEmailResponse(welcome_email_sent=sent, welcome_email_warning=warning)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def users_delete(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> None:
    delete_user(db, user_id, actor_id=admin.id)
