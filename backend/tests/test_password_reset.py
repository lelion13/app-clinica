from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.models.password_reset import PasswordResetToken
from app.models.user import User, UserRole
from app.services import password_reset_service as prs


def _user(*, active=True, user_id=1, email="a@example.com"):
    user = User(
        id=user_id,
        name="Ana",
        email=email,
        password_hash="hash",
        role=UserRole.operador,
        is_active=active,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    return user


def test_hash_token_stable():
    assert prs._hash_token("abc") == prs._hash_token("abc")
    assert prs._hash_token("abc") != prs._hash_token("abd")


def test_request_password_reset_skips_inactive():
    db = MagicMock()
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = _user(active=False)
    db.execute.return_value = execute_result

    with patch.object(prs, "_cooldown_allows", return_value=True):
        with patch.object(prs, "send_password_reset_email") as send_mail:
            prs.request_password_reset(db, email="a@example.com", client_key="ip1")

    db.add.assert_not_called()
    send_mail.assert_not_called()


def test_request_password_reset_skips_missing_user():
    db = MagicMock()
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = None
    db.execute.return_value = execute_result

    with patch.object(prs, "_cooldown_allows", return_value=True):
        with patch.object(prs, "send_password_reset_email") as send_mail:
            prs.request_password_reset(db, email="missing@example.com", client_key="ip1")

    db.add.assert_not_called()
    send_mail.assert_not_called()


def test_request_password_reset_sends_for_active():
    db = MagicMock()
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = _user(active=True)
    db.execute.return_value = execute_result

    with patch.object(prs, "_cooldown_allows", return_value=True):
        with patch.object(prs, "send_password_reset_email") as send_mail:
            prs.request_password_reset(db, email="a@example.com", client_key="ip1")

    db.add.assert_called_once()
    db.commit.assert_called()
    send_mail.assert_called_once()
    assert send_mail.call_args.kwargs["to_email"] == "a@example.com"
    assert "raw_token" in send_mail.call_args.kwargs


def test_reset_password_rejects_expired_token():
    db = MagicMock()
    row = PasswordResetToken(
        id=1,
        user_id=1,
        token_hash=prs._hash_token("tok"),
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
        used_at=None,
        created_at=datetime.now(timezone.utc),
    )
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = row
    db.execute.return_value = execute_result

    with pytest.raises(HTTPException) as exc:
        prs.reset_password_with_token(db, raw_token="tok", new_password="Password123")
    assert exc.value.status_code == 400


def test_reset_password_rejects_reuse():
    db = MagicMock()
    row = PasswordResetToken(
        id=1,
        user_id=1,
        token_hash=prs._hash_token("tok"),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        used_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = row
    db.execute.return_value = execute_result

    with pytest.raises(HTTPException) as exc:
        prs.reset_password_with_token(db, raw_token="tok", new_password="Password123")
    assert exc.value.status_code == 400


def test_reset_password_ok_marks_used():
    db = MagicMock()
    user = _user(active=True)
    row = PasswordResetToken(
        id=1,
        user_id=1,
        token_hash=prs._hash_token("tok"),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        used_at=None,
        created_at=datetime.now(timezone.utc),
    )
    first = MagicMock()
    first.scalar_one_or_none.return_value = row
    second = MagicMock()
    second.scalar_one_or_none.return_value = user
    db.execute.side_effect = [first, second]

    with patch("app.services.password_reset_service.hash_password", return_value="newhash"):
        prs.reset_password_with_token(db, raw_token="tok", new_password="Password123")

    assert user.password_hash == "newhash"
    assert row.used_at is not None
    db.commit.assert_called_once()
