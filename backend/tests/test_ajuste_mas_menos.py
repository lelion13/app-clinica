"""Unit tests for Ajuste +/- signed waterfill."""

from decimal import Decimal

from app.services.novedades import ajuste_mas_menos as adj
from app.services.novedades import importe_descontar as imp


def test_parse_monto_plus_sign():
    assert imp._parse_monto("+500") == Decimal("500")
    assert imp._parse_monto("500") == Decimal("500")
    assert imp._parse_monto("-500") == Decimal("-500")


def test_allocations_signed_positive_two_services():
    services = [(1, Decimal("1000")), (2, Decimal("800"))]
    got = adj._allocations_signed(services, Decimal("1500"), is_negative=False)
    assert got == [(1, Decimal("1000")), (2, Decimal("500"))]


def test_allocations_signed_negative_matches_descontar():
    services = [(1, Decimal("1000")), (2, Decimal("800"))]
    got = adj._allocations_signed(services, Decimal("1500"), is_negative=True)
    assert got == [(1, Decimal("-1000")), (2, Decimal("-500"))]


def test_allocations_signed_positive_solo_produccion():
    assert adj._allocations_signed([], Decimal("100"), is_negative=False) == [
        (None, Decimal("100"))
    ]


def test_comentario_positive_shape():
    signed = Decimal("500")
    comment = f"3904 - Juan Perez - Guardia - {signed}"[:500]
    assert comment.endswith("500")
    assert "-500" not in comment
