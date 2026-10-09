"""Unit tests for Índices hour signing helper."""

from decimal import Decimal

from app.services.novedades.indices import signed_horas


def test_signed_horas_extras_add():
    assert signed_horas("hora_extra", Decimal("4")) == Decimal("4")
    assert signed_horas("hora_extra_por_ausencia", Decimal("2")) == Decimal("2")


def test_signed_horas_descontar_subtracts():
    assert signed_horas("horas_a_descontar", Decimal("1")) == Decimal("-1")


def test_signed_horas_modulo_zero():
    assert signed_horas("modulo_asignado", Decimal("10")) == Decimal("0")


def test_signed_horas_none():
    assert signed_horas("hora_extra", None) == Decimal("0")
