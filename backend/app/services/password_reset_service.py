import hashlib
import logging
import secrets
import time
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models.password_reset import PasswordResetToken
from app.models.user import User
from app.services.email_service import send_password_reset_email

logger = logging.getLogger(__name__)

# In-memory cooldown: key -> monotonic timestamp of last attempt.
_forgot_cooldown: dict[str, float] = {}


def _hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _cooldown_allows(key: str) -> bool:
    now = time.monotonic()
    last = _forgot_cooldown.get(key)
    cooldown = max(0, int(settings.password_reset_cooldown_seconds))
    if last is not None and (now - last) < cooldown:
        return False
    _forgot_cooldown[key] = now
    # Opportunistic cleanup to avoid unbounded growth.
    if len(_forgot_cooldown) > 5000:
        cutoff = now - cooldown
        stale = [k for k, ts in _forgot_cooldown.items() if ts < cutoff]
        for k in stale:
            _forgot_cooldown.pop(k, None)
    return True


def request_password_reset(db: Session, *, email: str, client_key: str) -> None:
    """Always no-op from caller's perspective; send mail only for active users."""
    normalized = email.lower().strip()
    if not _cooldown_allows(f"{client_key}:{normalized}"):
        return

    user = db.execute(
        select(User).where(User.email == normalized, User.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not user or not user.is_active:
        return

    raw_token = secrets.token_urlsafe(32)
    now = _utcnow()
    row = PasswordResetToken(
        user_id=user.id,
        token_hash=_hash_token(raw_token),
        expires_at=now + timedelta(minutes=settings.password_reset_ttl_minutes),
        used_at=None,
        created_at=now,
    )
    db.add(row)
    db.commit()

    try:
        send_password_reset_email(to_email=user.email, name=user.name, raw_token=raw_token)
    except Exception:
        logger.exception("Failed to send password reset email to user_id=%s", user.id)


def reset_password_with_token(db: Session, *, raw_token: str, new_password: str) -> None:
    generic = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="El enlace no es válido o expiró",
    )
    token_hash = _hash_token(raw_token.strip())
    row = db.execute(
        select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
    ).scalar_one_or_none()
    if not row or row.used_at is not None:
        raise generic

    expires = row.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < _utcnow():
        raise generic

    user = db.execute(
        select(User).where(User.id == row.user_id, User.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not user or not user.is_active:
        raise generic

    user.password_hash = hash_password(new_password)
    user.updated_at = datetime.utcnow()
    row.used_at = _utcnow()
    db.commit()
