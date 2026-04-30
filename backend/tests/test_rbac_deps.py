import pytest
from fastapi import HTTPException

from app.api.deps import require_admin, require_operator_or_admin
from app.models.user import UserRole


class DummyUser:
    def __init__(self, role):
        self.role = role


def test_require_admin_allows_admin():
    user = DummyUser(UserRole.admin)
    assert require_admin(user) is user


def test_require_admin_blocks_operator():
    user = DummyUser(UserRole.operador)
    with pytest.raises(HTTPException) as exc:
        require_admin(user)
    assert exc.value.status_code == 403


def test_require_operator_or_admin_allows_operator():
    user = DummyUser(UserRole.operador)
    assert require_operator_or_admin(user) is user
