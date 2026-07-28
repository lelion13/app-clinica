from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.models.novedades import PeriodoEstado
from app.models.user import UserRole
from app.schemas.novedades import NovedadCreateRequest, PeriodoCreateRequest
from app.services.novedades import cargas as cargas_service
from app.services.novedades.helpers import assert_can_load_servicio, require_periodo_open


class FakeResult:
    def __init__(self, value):
        self._value = value

    def scalar_one_or_none(self):
        return self._value

    def scalars(self):
        return self

    def all(self):
        return self._value if isinstance(self._value, list) else []


class FakeDB:
    def __init__(self, mapping):
        self.mapping = mapping
        self.added = []
        self.committed = False

    def execute(self, _stmt):
        # Very small stub: callers pass through helpers that we monkeypatch in tests.
        return FakeResult(None)

    def add(self, item):
        self.added.append(item)

    def commit(self):
        self.committed = True

    def refresh(self, item):
        if getattr(item, "id", None) is None:
            item.id = 1


def test_require_periodo_open_blocks_closed(monkeypatch):
    closed = SimpleNamespace(id=1, estado=PeriodoEstado.closed, deleted_at=None)

    class DB:
        def execute(self, _stmt):
            return FakeResult(closed)

    with pytest.raises(HTTPException) as exc:
        require_periodo_open(DB(), 1)
    assert exc.value.status_code == 409


def test_assert_can_load_servicio_blocks_unscoped_jefe(monkeypatch):
    user = SimpleNamespace(id=9, role=UserRole.jefe_medico)

    class DB:
        def execute(self, _stmt):
            return FakeResult(None)

    with pytest.raises(HTTPException) as exc:
        assert_can_load_servicio(DB(), user, servicio_id=3)
    assert exc.value.status_code == 403


def test_create_periodo_rejects_second_open(monkeypatch):
    db = FakeDB({})
    monkeypatch.setattr(cargas_service, "get_open_periodo", lambda _db: SimpleNamespace(id=99))
    payload = PeriodoCreateRequest(
        nombre="P2",
        fecha_inicio=date(2026, 7, 1),
        fecha_fin=date(2026, 7, 31),
        open_now=True,
    )
    with pytest.raises(HTTPException) as exc:
        cargas_service.create_periodo(db, payload, actor_id=1)
    assert exc.value.status_code == 409


def test_create_novedad_requires_justificacion():
    user = SimpleNamespace(id=1, role=UserRole.admin)
    payload = NovedadCreateRequest.model_construct(
        periodo_id=1,
        servicio_id=1,
        professional_id=1,
        modulo_id=1,
        valor=Decimal("100.00"),
        justificacion="   ",
    )
    with pytest.raises(HTTPException) as exc:
        cargas_service.create_novedad(FakeDB({}), payload, user=user)
    assert exc.value.status_code == 422


def test_export_xlsx_content_type_bytes(monkeypatch):
    from app.services.novedades import export_xls

    monkeypatch.setattr(
        export_xls,
        "build_grid_rows",
        lambda *args, **kwargs: [],
    )
    content = export_xls.export_xlsx_bytes(FakeDB({}))
    assert isinstance(content, (bytes, bytearray))
    assert content[:2] == b"PK"  # zip/xlsx signature
