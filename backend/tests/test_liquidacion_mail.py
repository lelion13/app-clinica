from decimal import Decimal

from app.schemas.novedades import CapitalHumanoRowResponse
from app.services.novedades.liquidacion_mail import build_liquidacion_body, is_valid_email


def test_is_valid_email():
    assert is_valid_email("aaa@bbb.com")
    assert is_valid_email("  a@b.co  ")
    assert not is_valid_email(None)
    assert not is_valid_email("")
    assert not is_valid_email("sin-arroba")
    assert not is_valid_email("@dominio.com")
    assert not is_valid_email("a@b")


def test_build_liquidacion_body_includes_total():
    row = CapitalHumanoRowResponse(
        professional_id=1,
        legajo="6126",
        professional_name="BELLIDO JULIO CESAR",
        monto_cargas=Decimal("1000.00"),
        monto_ajustes=Decimal("-50.00"),
        monto_bonos=200,
        monto_practicas=0,
        monto_internaciones=0,
        monto_total=Decimal("1150.00"),
        bonos={"DEA|x": 2},
        bonos_subtotales={"DEA|x": 200},
    )
    text, html = build_liquidacion_body(
        periodo_nombre="Septiembre 2026",
        row=row,
        cargas=[],
        ajustes=[],
    )
    assert "Importe a facturar" in text
    assert "Total general" in text
    assert "Septiembre 2026" in text
    assert "BELLIDO" in text
    assert "1.150,00" in text
    assert "Importe a facturar" in html
    assert "<h3>Cargas</h3>" in html
