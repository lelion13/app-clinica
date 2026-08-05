import pytest
from pydantic import ValidationError

from app.schemas.location import LocationCreateRequest, LocationUpdateRequest


def test_create_requires_tipo():
    with pytest.raises(ValidationError):
        LocationCreateRequest(name="Sede", id_dominio=1651, tipo="")
    with pytest.raises(ValidationError):
        LocationCreateRequest(name="Sede", id_dominio=1651, tipo="   ")


def test_create_strips_tipo():
    item = LocationCreateRequest(name="Sede", id_dominio=1651, tipo="  SEDE TORRE  ")
    assert item.tipo == "SEDE TORRE"


def test_update_requires_tipo():
    with pytest.raises(ValidationError):
        LocationUpdateRequest(name="Sede", id_dominio=1651, tipo="")
    ok = LocationUpdateRequest(name="Sede", id_dominio=1651, tipo="SEDE TORRE")
    assert ok.tipo == "SEDE TORRE"
