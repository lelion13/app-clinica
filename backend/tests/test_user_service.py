from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.models.user import User, UserRole
from app.schemas.user import UserCreateRequest, UserUpdateRequest
from app.services import user_service


def _user(**overrides):
    data = dict(
        id=1,
        name="Ana",
        email="ana@example.com",
        password_hash="old",
        role=UserRole.operador,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        deleted_at=None,
    )
    data.update(overrides)
    return User(**data)


def test_create_user_returns_welcome_warning_when_mail_fails():
    db = MagicMock()
    missing = MagicMock()
    missing.scalar_one_or_none.return_value = None
    db.execute.return_value = missing

    payload = UserCreateRequest(
        name="Ana Test",
        email="ana@example.com",
        password="Password123",
        role="operador",
    )

    with patch("app.services.user_service.hash_password", return_value="hashed"):
        with patch("app.services.user_service.send_welcome_email", side_effect=RuntimeError("smtp")):
            user, sent, warning = user_service.create_user(db, payload, actor_id=9)

    assert user.email == "ana@example.com"
    assert sent is False
    assert warning is not None
    db.commit.assert_called()


def test_update_user_optional_password():
    db = MagicMock()
    user = _user()
    found = MagicMock()
    found.scalar_one_or_none.return_value = user
    db.execute.return_value = found

    payload = UserUpdateRequest(password="Password999")
    with patch("app.services.user_service.hash_password", return_value="newhash") as hp:
        updated = user_service.update_user(db, 1, payload, actor_id=2)

    hp.assert_called_once_with("Password999")
    assert updated.password_hash == "newhash"


def test_update_user_email_conflict():
    db = MagicMock()
    user = _user(id=1, email="a@example.com")
    conflict = _user(id=2, email="b@example.com")
    first = MagicMock()
    first.scalar_one_or_none.return_value = user
    second = MagicMock()
    second.scalar_one_or_none.return_value = conflict
    db.execute.side_effect = [first, second]

    with pytest.raises(HTTPException) as exc:
        user_service.update_user(
            db,
            1,
            UserUpdateRequest(email="b@example.com"),
            actor_id=2,
        )
    assert exc.value.status_code == 409
