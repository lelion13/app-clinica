from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.services.setup_service import bootstrap_admin


def _fake_db_with_user_count(user_count: int):
    db = MagicMock()
    execute_result = MagicMock()
    execute_result.scalar_one.return_value = user_count
    db.execute.return_value = execute_result
    return db


def test_bootstrap_admin_blocked_when_user_exists():
    db = _fake_db_with_user_count(1)

    with pytest.raises(HTTPException) as exc:
        bootstrap_admin(db, "Admin", "admin@example.com", "Password123")

    assert exc.value.status_code == 403
    assert "Setup deshabilitado" in str(exc.value.detail)


def test_bootstrap_admin_creates_user_when_no_users():
    db = _fake_db_with_user_count(0)

    user = bootstrap_admin(db, "Admin", "admin@example.com", "Password123")

    assert user.email == "admin@example.com"
    assert user.role.value == "admin"
    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
