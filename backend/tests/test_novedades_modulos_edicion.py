from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.schemas.novedades import (
    ModuloCreateRequest,
    ModuloServiciosUpdateRequest,
    ModuloUpdateRequest,
)
from app.services.novedades import masters as masters_service


def test_modulo_create_default_produccion_false():
    payload = ModuloCreateRequest(
        descripcion="Mod A",
        valor=Decimal("100"),
        servicio_ids=[1],
    )
    assert payload.produccion is False


def test_modulo_update_sin_servicio_ids():
    payload = ModuloUpdateRequest(
        descripcion="Mod B",
        comentario=None,
        valor=Decimal("200"),
        produccion=True,
    )
    assert payload.produccion is True
    assert not hasattr(payload, "servicio_ids") or "servicio_ids" not in payload.model_fields_set


def test_modulo_servicios_permite_vacio():
    payload = ModuloServiciosUpdateRequest(servicio_ids=[])
    assert payload.servicio_ids == []


def test_update_modulo_no_toca_servicios(monkeypatch):
    item = SimpleNamespace(
        id=5,
        descripcion="old",
        comentario=None,
        valor=Decimal("10"),
        produccion=False,
        deleted_at=None,
        updated_at=None,
        updated_by=None,
    )

    class DB:
        def execute(self, _stmt):
            return SimpleNamespace(scalar_one_or_none=lambda: item)

        def commit(self):
            pass

        def refresh(self, _item):
            pass

    called = {"set": False}
    monkeypatch.setattr(
        masters_service,
        "_set_modulo_servicios",
        lambda *_a, **_k: called.__setitem__("set", True),
    )
    payload = ModuloUpdateRequest(
        descripcion="nuevo",
        comentario="c",
        valor=Decimal("50"),
        produccion=True,
    )
    out = masters_service.update_modulo(DB(), 5, payload, actor_id=1)
    assert out.descripcion == "nuevo"
    assert out.produccion is True
    assert called["set"] is False


def test_update_modulo_servicios_vacio(monkeypatch):
    item = SimpleNamespace(id=5, deleted_at=None, updated_at=None, updated_by=None)
    set_args = {}

    class DB:
        def execute(self, _stmt):
            return SimpleNamespace(scalar_one_or_none=lambda: item)

        def commit(self):
            pass

        def refresh(self, _item):
            pass

    monkeypatch.setattr(
        masters_service,
        "_validate_servicio_ids",
        lambda _db, ids, allow_empty=False: list(ids),
    )
    monkeypatch.setattr(
        masters_service,
        "_set_modulo_servicios",
        lambda _db, mid, ids, actor: set_args.update({"mid": mid, "ids": ids, "actor": actor}),
    )
    out = masters_service.update_modulo_servicios(DB(), 5, [], actor_id=9)
    assert out is item
    assert set_args == {"mid": 5, "ids": [], "actor": 9}


def test_update_modulo_servicios_404():
    class DB:
        def execute(self, _stmt):
            return SimpleNamespace(scalar_one_or_none=lambda: None)

    with pytest.raises(HTTPException) as exc:
        masters_service.update_modulo_servicios(DB(), 99, [1], actor_id=1)
    assert exc.value.status_code == 404
