"""Unit tests for Valores Extras filter helpers."""

from datetime import date, datetime
from decimal import Decimal

from app.schemas.novedades import GridRowResponse
from app.services.novedades.valores_extras import (
    professional_matches_q,
    row_has_observacion,
    row_matches_filtro,
)


def _row(**kwargs) -> GridRowResponse:
    base = dict(
        tipo="hora_extra",
        id=1,
        periodo_id=1,
        periodo_nombre="P",
        servicio_id=1,
        servicio_nombre="Serv",
        professional_id=1,
        professional_name="Ana",
        legajo="100",
        concepto="Hora extra",
        horas=Decimal("2"),
        valor=Decimal("100"),
        valor_hora=Decimal("50"),
        cargado_por=None,
        fecha_realizacion=date(2026, 10, 1),
        fecha_carga=datetime(2026, 10, 2),
        motivo_sin_produccion=None,
        observacion_sin_produccion=None,
    )
    base.update(kwargs)
    return GridRowResponse(**base)


def test_filtro_ambos_incluye_todo():
    assert row_matches_filtro(_row(tipo="modulo_asignado"), "ambos")
    assert row_matches_filtro(_row(tipo="hora_extra"), "ambos")


def test_filtro_modulos_y_novedades():
    mod = _row(tipo="modulo_asignado", horas=None, valor_hora=None)
    nov = _row(tipo="hora_extra")
    assert row_matches_filtro(mod, "modulos")
    assert not row_matches_filtro(nov, "modulos")
    assert row_matches_filtro(nov, "novedades")
    assert not row_matches_filtro(mod, "novedades")


def test_novedad_extra_requiere_observacion():
    sin = _row(motivo_sin_produccion="vacaciones", observacion_sin_produccion=None)
    con = _row(observacion_sin_produccion="  texto  ")
    assert not row_has_observacion(sin)
    assert not row_matches_filtro(sin, "novedad_extra")
    assert row_has_observacion(con)
    assert row_matches_filtro(con, "novedad_extra")
    assert row_matches_filtro(_row(tipo="modulo_asignado", observacion_sin_produccion="x"), "novedad_extra")


def test_professional_matches_q_nombre_y_legajo():
    assert professional_matches_q(name="Ana Pérez", legajo="123", q=None)
    assert professional_matches_q(name="Ana Pérez", legajo="123", q="pérez")
    assert professional_matches_q(name="Ana Pérez", legajo="123", q="123")
    assert not professional_matches_q(name="Ana Pérez", legajo="123", q="zzz")
