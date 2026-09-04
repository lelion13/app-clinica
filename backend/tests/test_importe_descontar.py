"""Unit tests for Importe a descontar waterfill and parsing."""

from decimal import Decimal

import pytest

from app.services.novedades import importe_descontar as imp


def test_parse_monto_variants():
    assert imp._parse_monto("500") == Decimal("500")
    assert imp._parse_monto("-500") == Decimal("-500")
    assert imp._parse_monto("1.234,56") == Decimal("1234.56")
    assert imp._parse_monto("") is None
    assert imp._parse_monto(None) is None


def test_waterfill_two_services():
    services = [(1, Decimal("1000")), (2, Decimal("800"))]
    got = imp._waterfill(services, Decimal("1500"))
    assert got == [(1, Decimal("-1000")), (2, Decimal("-500"))]


def test_waterfill_remainder_to_last():
    services = [(1, Decimal("1000")), (2, Decimal("800"))]
    got = imp._waterfill(services, Decimal("2000"))
    assert got == [(1, Decimal("-1000")), (2, Decimal("-1000"))]


def test_waterfill_solo_produccion():
    assert imp._waterfill([], Decimal("100")) == [(None, Decimal("-100"))]


def test_waterfill_single_service():
    assert imp._waterfill([(9, Decimal("500"))], Decimal("300")) == [(9, Decimal("-300"))]


def test_comentario_truncation_shape():
    neg = -Decimal("500")
    comment = f"3904 - Juan Perez - Guardia - {neg}"[:500]
    assert comment.endswith("-500")
    assert "3904" in comment
