from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.models.novedades import NovedadTipo
from app.schemas.novedades import FeriadoCreateRequest, ModuloCreateRequest, NovedadCreateRequest
from app.services.novedades.helpers import novedad_valor_calculado
from app.services.novedades import masters as masters_service


def test_novedad_valor_positivo():
    assert novedad_valor_calculado(NovedadTipo.hora_extra, 3, Decimal("1000")) == Decimal("3000")


def test_novedad_valor_horas_a_descontar():
    assert novedad_valor_calculado("horas_a_descontar", 3, Decimal("1000")) == Decimal("-3000")


def test_novedad_create_acepta_horas_a_descontar():
    payload = NovedadCreateRequest(
        periodo_id=1,
        servicio_id=1,
        professional_id=1,
        tipo="horas_a_descontar",
        horas=2,
        fecha_realizacion=date(2026, 8, 16),
    )
    assert payload.tipo == "horas_a_descontar"


def test_modulo_create_default_sadofe_false():
    payload = ModuloCreateRequest(
        descripcion="Mod A",
        valor=Decimal("100"),
        servicio_ids=[1],
    )
    assert payload.sadofe is False


def test_create_feriado_rechaza_fecha_duplicada(monkeypatch):
    monkeypatch.setattr(masters_service, "_feriado_fecha_taken", lambda *_a, **_k: True)
    db = SimpleNamespace()
    payload = FeriadoCreateRequest(fecha=date(2026, 12, 25), nombre="Navidad")
    with pytest.raises(HTTPException) as exc:
        masters_service.create_feriado(db, payload, actor_id=1)
    assert exc.value.status_code == 409
