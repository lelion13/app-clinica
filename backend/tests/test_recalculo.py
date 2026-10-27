from decimal import Decimal

from app.services.novedades.helpers import novedad_valor_calculado
from app.services.novedades.prof_sync import modulo_valor_para_profesional
from app.services.novedades.recalculo import _money_eq


def test_money_eq():
    assert _money_eq(Decimal("10.00"), Decimal("10"))
    assert not _money_eq(Decimal("10.00"), Decimal("10.01"))


def test_modulo_plus_for_recalculo():
    assert modulo_valor_para_profesional(
        Decimal("1000"), es_especialista=True, servicio_especialista=True
    ) == Decimal("1200.00")
    assert modulo_valor_para_profesional(
        Decimal("1000"), es_especialista=True, servicio_especialista=False
    ) == Decimal("1000")


def test_horas_importe_sign():
    assert novedad_valor_calculado("hora_extra", 3, Decimal("1100")) == Decimal("3300")
    assert novedad_valor_calculado("horas_a_descontar", 2, Decimal("1000")) == Decimal("-2000")
