import pytest
from fastapi import HTTPException

from app.api.deps import (
    require_admin,
    require_admin_or_jefe,
    require_admin_or_rrhh,
    require_novedades_reader,
    require_operator_or_admin,
)
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


def test_require_admin_or_rrhh_allows_rrhh():
    user = DummyUser(UserRole.rrhh)
    assert require_admin_or_rrhh(user) is user


def test_require_admin_or_rrhh_blocks_jefe():
    user = DummyUser(UserRole.jefe_medico)
    with pytest.raises(HTTPException) as exc:
        require_admin_or_rrhh(user)
    assert exc.value.status_code == 403


def test_require_admin_or_jefe_allows_jefe():
    user = DummyUser(UserRole.jefe_medico)
    assert require_admin_or_jefe(user) is user


def test_require_admin_or_jefe_blocks_rrhh():
    user = DummyUser(UserRole.rrhh)
    with pytest.raises(HTTPException) as exc:
        require_admin_or_jefe(user)
    assert exc.value.status_code == 403


def test_require_novedades_reader_blocks_operador():
    user = DummyUser(UserRole.operador)
    with pytest.raises(HTTPException) as exc:
        require_novedades_reader(user)
    assert exc.value.status_code == 403


def test_new_roles_enum_values():
    assert UserRole.jefe_medico.value == "jefe_medico"
    assert UserRole.rrhh.value == "rrhh"
