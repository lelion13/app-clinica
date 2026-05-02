from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from app.core.config import settings

# bcrypt operates on at most 72 bytes of password material (RFC historical limit).
_BCRYPT_MAX_PW_BYTES = 72


def hash_password(password: str) -> str:
    pw = password.encode("utf-8")
    if len(pw) > _BCRYPT_MAX_PW_BYTES:
        raise ValueError("password exceeds bcrypt limit of 72 bytes")
    salt = bcrypt.gensalt(rounds=settings.bcrypt_rounds)
    return bcrypt.hashpw(pw, salt).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False


def _create_token(subject: str, role: str, token_type: str, expires_minutes: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "role": role,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def create_access_token(subject: str, role: str) -> str:
    return _create_token(subject, role, "access", settings.jwt_access_minutes)


def create_refresh_token(subject: str, role: str) -> str:
    refresh_minutes = settings.jwt_refresh_days * 24 * 60
    return _create_token(subject, role, "refresh", refresh_minutes)
