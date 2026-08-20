from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import ForgotPasswordRequest, LoginRequest, MeResponse, ResetPasswordRequest
from app.services.auth_service import authenticate_user, decode_token, issue_tokens
from app.services.password_reset_service import request_password_reset, reset_password_with_token

router = APIRouter()


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.jwt_access_minutes * 60,
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.jwt_refresh_days * 24 * 60 * 60,
    )


def _client_key(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip() or "unknown"
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


@router.post("/login", status_code=status.HTTP_204_NO_CONTENT)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> None:
    user = authenticate_user(db, payload.email, payload.password)
    access_token, refresh_token = issue_tokens(user)
    _set_auth_cookies(response, access_token, refresh_token)


@router.post("/forgot-password", status_code=status.HTTP_204_NO_CONTENT)
def forgot_password(
    payload: ForgotPasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> None:
    request_password_reset(db, email=payload.email, client_key=_client_key(request))


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)) -> None:
    reset_password_with_token(db, raw_token=payload.token, new_password=payload.password)


@router.post("/refresh", status_code=status.HTTP_204_NO_CONTENT)
def refresh(response: Response, refresh_token: str | None = Cookie(default=None), db: Session = Depends(get_db)) -> None:
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")
    payload = decode_token(refresh_token, expected_type="refresh")
    user = db.execute(select(User).where(User.id == int(payload["sub"]), User.deleted_at.is_(None))).scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")
    access_token, new_refresh_token = issue_tokens(user)
    _set_auth_cookies(response, access_token, new_refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")


@router.get("/me", response_model=MeResponse)
def me(user: User = Depends(current_user)) -> MeResponse:
    return MeResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role.value,
        is_active=user.is_active,
    )
