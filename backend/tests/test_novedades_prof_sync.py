from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.models.user import UserRole
from app.services.novedades import purge as purge_service
from app.services.novedades.helpers import get_professional_or_404
from app.services.novedades import prof_sync as prof_sync_service


class FakeResult:
    def __init__(self, value):
        self._value = value
        self.rowcount = value if isinstance(value, int) else 0

    def scalar_one_or_none(self):
        return self._value

    def scalars(self):
        return self

    def all(self):
        return self._value if isinstance(self._value, list) else []


class SyncFakeDB:
    def __init__(self, existing=None):
        self.existing = list(existing or [])
        self.added = []
        self.committed = False

    def execute(self, _stmt):
        return FakeResult(self.existing)

    def add(self, item):
        self.added.append(item)
        self.existing.append(item)

    def commit(self):
        self.committed = True


def test_normalize_preserves_leading_zeros():
    assert prof_sync_service._normalize_row(
        {"CODPROF": "001", "NOMBRES": "A", "CODPROV": "0001", "LEGAJO": " 05100"}
    ) == (
        "001",
        "A",
        "0001",
        "05100",
    )


def test_normalize_legajo_optional():
    assert prof_sync_service._normalize_row({"CODPROF": "032", "NOMBRES": "X", "CODPROV": "0032"}) == (
        "032",
        "X",
        "0032",
        None,
    )


def test_sync_inactivates_missing_and_reactivates(monkeypatch):
    inactive = SimpleNamespace(
        codprof="001",
        full_name="OLD",
        codprov="0001",
        legajo=None,
        is_active=False,
        deleted_at=None,
        updated_at=None,
        updated_by=None,
    )
    active_gone = SimpleNamespace(
        codprof="002",
        full_name="Gone",
        codprov=None,
        legajo=None,
        is_active=True,
        deleted_at=None,
        updated_at=None,
        updated_by=None,
    )
    db = SyncFakeDB([inactive, active_gone])
    monkeypatch.setattr(
        prof_sync_service,
        "_fetch_remote_rows",
        lambda: [{"CODPROF": "001", "NOMBRES": "NEW NAME", "CODPROV": "0009", "LEGAJO": "05100"}],
    )
    result = prof_sync_service.sync_novedades_professionals(db, actor_id=7)
    assert inactive.is_active is True
    assert inactive.full_name == "NEW NAME"
    assert inactive.codprov == "0009"
    assert inactive.legajo == "05100"
    assert active_gone.is_active is False
    assert result.updated >= 1
    assert result.inactivated == 1
    assert db.committed


def test_sync_does_not_inactivate_when_fetch_fails(monkeypatch):
    row = SimpleNamespace(
        codprof="001", full_name="A", codprov=None, legajo=None, is_active=True, deleted_at=None
    )
    db = SyncFakeDB([row])

    def boom():
        raise HTTPException(status_code=502, detail="down")

    monkeypatch.setattr(prof_sync_service, "_fetch_remote_rows", boom)
    with pytest.raises(HTTPException) as exc:
        prof_sync_service.sync_novedades_professionals(db, actor_id=1)
    assert exc.value.status_code == 502
    assert row.is_active is True


def test_get_professional_rejects_inactive():
    inactive = SimpleNamespace(id=3, is_active=False, deleted_at=None)

    class DB:
        def execute(self, _stmt):
            return FakeResult(inactive)

    with pytest.raises(HTTPException) as exc:
        get_professional_or_404(DB(), 3, require_active=True)
    assert exc.value.status_code == 422


def test_purge_blocks_jefe():
    user = SimpleNamespace(id=1, role=UserRole.jefe_medico)
    with pytest.raises(HTTPException) as exc:
        purge_service.purge_novedades_transaccional(MagicMock(), user=user)
    assert exc.value.status_code == 403


def test_purge_admin_counts(monkeypatch):
    user = SimpleNamespace(id=1, role=UserRole.admin)
    calls = {"n": 0}

    class DB:
        def execute(self, _stmt):
            calls["n"] += 1
            return FakeResult(calls["n"])  # rowcount via FakeResult for delete

        def commit(self):
            return None

    # delete().rowcount — our FakeResult uses value as rowcount when int
    result = purge_service.purge_novedades_transaccional(DB(), user=user)
    assert result.deleted_asignaciones == 1
    assert result.deleted_novedades == 2
    assert result.deleted_profesional_servicios == 3


def test_apply_especialistas_match_and_unmatched(monkeypatch):
    known = SimpleNamespace(
        codprof="1099",
        full_name="A",
        es_especialista=False,
        deleted_at=None,
        updated_at=None,
        updated_by=None,
    )
    other = SimpleNamespace(
        codprof="2000",
        full_name="B",
        es_especialista=True,
        deleted_at=None,
        updated_at=None,
        updated_by=None,
    )
    db = SyncFakeDB([known, other])
    monkeypatch.setattr(
        prof_sync_service,
        "_fetch_especialistas_rows",
        lambda: [
            {"profesional": "1099", "descripcion": "Dr A"},
            {"profesional": "9999", "descripcion": "Ghost"},
        ],
    )
    matched, unmatched, warning = prof_sync_service.apply_especialistas_flags(db, actor_id=1)
    assert warning is None
    assert matched == 1
    assert known.es_especialista is True
    assert other.es_especialista is False
    assert len(unmatched) == 1
    assert unmatched[0].profesional == "9999"
    assert unmatched[0].descripcion == "Ghost"


def test_apply_especialistas_fail_preserves_flags(monkeypatch):
    row = SimpleNamespace(
        codprof="1099",
        es_especialista=True,
        deleted_at=None,
        updated_at=None,
        updated_by=None,
    )
    db = SyncFakeDB([row])

    def boom():
        raise HTTPException(status_code=502, detail="especialistas down")

    monkeypatch.setattr(prof_sync_service, "_fetch_especialistas_rows", boom)
    matched, unmatched, warning = prof_sync_service.apply_especialistas_flags(db, actor_id=1)
    assert matched == 0
    assert unmatched == []
    assert warning
    assert row.es_especialista is True


def test_sync_with_especialistas_param(monkeypatch):
    row = SimpleNamespace(
        codprof="001",
        full_name="A",
        codprov=None,
        legajo=None,
        is_active=True,
        es_especialista=False,
        deleted_at=None,
        updated_at=None,
        updated_by=None,
    )
    db = SyncFakeDB([row])
    monkeypatch.setattr(
        prof_sync_service,
        "_fetch_remote_rows",
        lambda: [{"CODPROF": "001", "NOMBRES": "A", "CODPROV": "1"}],
    )
    monkeypatch.setattr(
        prof_sync_service,
        "_fetch_especialistas_rows",
        lambda: [{"profesional": "001", "descripcion": "A"}],
    )
    result = prof_sync_service.sync_novedades_professionals(db, actor_id=1, sync_especialistas=True)
    assert row.es_especialista is True
    assert result.especialistas_matched == 1
    assert result.especialistas_warning is None
