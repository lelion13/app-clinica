from app.services.novedades.produccion_tarifas import valorize_bonos


def test_valorize_bonos_with_tarifa():
    bonos = {"CMG|CAP|LUNES_VIERNES|DIA": 3}
    tarifas = {"CMG|CAP|LUNES_VIERNES|DIA": 1000}
    subtotales, total = valorize_bonos(bonos, tarifas)
    assert subtotales == {"CMG|CAP|LUNES_VIERNES|DIA": 3000}
    assert total == 3000


def test_valorize_bonos_sin_tarifa():
    bonos = {"CMG|CLINICA|LUNES_VIERNES|DIA": 5}
    subtotales, total = valorize_bonos(bonos, {})
    assert subtotales == {"CMG|CLINICA|LUNES_VIERNES|DIA": 0}
    assert total == 0


def test_valorize_bonos_empty():
    subtotales, total = valorize_bonos(None, {"k": 10})
    assert subtotales == {}
    assert total == 0
