import pytest
from fastapi import HTTPException

from app.services.novedades import tiene_produccion as tp


def test_parse_bool_variants():
    assert tp.parse_tiene_produccion_payload(True) is True
    assert tp.parse_tiene_produccion_payload(False) is False
    assert tp.parse_tiene_produccion_payload("true") is True
    assert tp.parse_tiene_produccion_payload("FALSE") is False
    assert tp.parse_tiene_produccion_payload({"tiene_produccion": True}) is True
    assert tp.parse_tiene_produccion_payload({"data": False}) is False


def test_parse_rejects_unknown():
    with pytest.raises(HTTPException) as exc:
        tp.parse_tiene_produccion_payload({"foo": "bar"})
    assert exc.value.status_code == 502


def test_check_requires_params(monkeypatch):
    with pytest.raises(HTTPException) as exc:
        tp.check_tiene_produccion(fecha="", codprof="1265")
    assert exc.value.status_code == 422


def test_check_requires_config(monkeypatch):
    monkeypatch.setattr(tp.settings, "novedades_bonos_tiene_produccion_url", "")
    monkeypatch.setattr(tp.settings, "novedades_prof_sync_token", "")
    with pytest.raises(HTTPException) as exc:
        tp.check_tiene_produccion(fecha="2026-08-03", codprof="1265")
    assert exc.value.status_code == 422
