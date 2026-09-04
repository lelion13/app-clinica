"""Unit tests for liquidación XLS export builder."""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.models.novedades import PeriodoEstado
from app.services.novedades import liquidacion_export as liq


class FakeResult:
    def __init__(self, value):
        self._value = value

    def scalar_one_or_none(self):
        return self._value

    def scalars(self):
        return self

    def all(self):
        if self._value is None:
            return []
        if isinstance(self._value, list):
            return self._value
        return [self._value]

    def first(self):
        return self.scalar_one_or_none()


def test_empresa_from_concepto():
    assert liq.empresa_from_concepto(50) == "CMG"
    assert liq.empresa_from_concepto(100) == "CMG"
    assert liq.empresa_from_concepto(101) == "CHI"
    assert liq.empresa_from_concepto(123) == "CHI"


def test_empresa_from_prefix():
    assert liq.empresa_from_prefix("CMG") == "CMG"
    assert liq.empresa_from_prefix("cmg-oeste") == "CMG"
    assert liq.empresa_from_prefix("SC") == "CHI"
    assert liq.empresa_from_prefix("scchi") == "CHI"
    assert liq.empresa_from_prefix("") == "CMG"
    assert liq.empresa_from_prefix(None) == "CMG"


def test_split_equal():
    assert liq._split_equal(Decimal("1000"), [50, 60]) == {50: Decimal("500"), 60: Decimal("500")}
    assert liq._split_equal(Decimal("0"), [50]) == {}
    assert liq._split_equal(Decimal("100"), []) == {}


def test_open_period_rejected(monkeypatch):
    periodo = SimpleNamespace(id=1, estado=PeriodoEstado.open, deleted_at=None)

    class DB:
        def execute(self, _stmt):
            return FakeResult(periodo)

    with pytest.raises(HTTPException) as exc:
        liq.build_liquidacion_rows(DB(), periodo_id=1)
    assert exc.value.status_code == 409


def test_missing_concepto_blocks(monkeypatch):
    periodo = SimpleNamespace(id=1, estado=PeriodoEstado.closed, deleted_at=None)
    svc = SimpleNamespace(id=10, nombre="Guardia", concepto_liquidacion=None)
    row = SimpleNamespace(
        professional_id=1,
        servicio_id=10,
        valor=Decimal("100"),
        tipo="modulo_asignado",
    )

    class DB:
        def __init__(self):
            self.n = 0

        def execute(self, _stmt):
            self.n += 1
            if self.n == 1:
                return FakeResult(periodo)
            return FakeResult([svc])

    monkeypatch.setattr(liq, "build_grid_rows", lambda *_a, **_k: [row])

    with pytest.raises(HTTPException) as exc:
        liq.build_liquidacion_rows(DB(), periodo_id=1)
    assert exc.value.status_code == 422
    assert "Guardia" in str(exc.value.detail)


def test_multi_concepto_cargas_and_prod_split(monkeypatch):
    periodo = SimpleNamespace(id=1, estado=PeriodoEstado.closed, deleted_at=None)
    svc50 = SimpleNamespace(id=10, nombre="S50", concepto_liquidacion=50)
    svc60 = SimpleNamespace(id=11, nombre="S60", concepto_liquidacion=60)
    rows = [
        SimpleNamespace(professional_id=1, servicio_id=10, valor=Decimal("100"), tipo="modulo_asignado"),
        SimpleNamespace(professional_id=1, servicio_id=11, valor=Decimal("200"), tipo="modulo_asignado"),
    ]
    prof = SimpleNamespace(id=1, legajo="3904", full_name="Test", deleted_at=None)
    queue = [
        FakeResult(periodo),
        FakeResult([svc50, svc60]),
        FakeResult([]),
        FakeResult([prof]),
    ]

    class DB:
        def execute(self, _stmt):
            return queue.pop(0)

    monkeypatch.setattr(liq, "build_grid_rows", lambda *_a, **_k: rows)

    # Patch snapshot loaders inside function via bonos_import module
    import app.services.novedades.bonos_import as bi

    monkeypatch.setattr(bi, "load_bonos_snapshot", lambda *_a, **_k: ([], {1: {"CMG|GUA|S|H": 10}}))
    monkeypatch.setattr(bi, "load_practicas_snapshot", lambda *_a, **_k: {})
    monkeypatch.setattr(bi, "load_internaciones_snapshot", lambda *_a, **_k: {})
    monkeypatch.setattr(liq, "load_tarifas_by_opcion_key", lambda *_a, **_k: {"CMG|GUA|S|H": 100})
    # 10 * 100 = 1000 producción CMG → split 500/500 on conceptos 50 y 60

    result = liq.build_liquidacion_rows(DB(), periodo_id=1)
    by_c = {r.concepto: r for r in result}
    assert by_c[50].empresa == "CMG"
    assert by_c[50].legajo == "3904"
    assert by_c[50].monto == Decimal("600")  # 100 + 500
    assert by_c[60].monto == Decimal("700")  # 200 + 500


def test_prod_other_empresa_falls_back_to_all_cargas(monkeypatch):
    """Q8=C: SC production with only CMG carga conceptos → split across those."""
    periodo = SimpleNamespace(id=1, estado=PeriodoEstado.closed, deleted_at=None)
    svc50 = SimpleNamespace(id=10, nombre="S50", concepto_liquidacion=50)
    rows = [
        SimpleNamespace(professional_id=1, servicio_id=10, valor=Decimal("0"), tipo="modulo_asignado"),
    ]
    prof = SimpleNamespace(id=1, legajo="1", full_name="P", deleted_at=None)
    queue = [
        FakeResult(periodo),
        FakeResult([svc50]),
        FakeResult([]),  # ajustes
        FakeResult([prof]),
    ]

    class DB:
        def execute(self, _stmt):
            return queue.pop(0)

    monkeypatch.setattr(liq, "build_grid_rows", lambda *_a, **_k: rows)
    import app.services.novedades.bonos_import as bi

    monkeypatch.setattr(bi, "load_bonos_snapshot", lambda *_a, **_k: ([], {1: {"SC|GUA|S|H": 5}}))
    monkeypatch.setattr(bi, "load_practicas_snapshot", lambda *_a, **_k: {})
    monkeypatch.setattr(bi, "load_internaciones_snapshot", lambda *_a, **_k: {})
    monkeypatch.setattr(liq, "load_tarifas_by_opcion_key", lambda *_a, **_k: {"SC|GUA|S|H": 200})
    # 5*200=1000 CHI prod → only CMG concepto 50 → all goes to 50

    result = liq.build_liquidacion_rows(DB(), periodo_id=1)
    assert len(result) == 1
    assert result[0].concepto == 50
    assert result[0].monto == Decimal("1000")


def test_solo_dea_cmg_fixed_concepto(monkeypatch):
    periodo = SimpleNamespace(id=1, estado=PeriodoEstado.closed, deleted_at=None)
    prof = SimpleNamespace(id=2, legajo="200", full_name="Solo", deleted_at=None)
    queue = [
        FakeResult(periodo),
        FakeResult([]),  # ajustes
        FakeResult([prof]),
    ]

    class DB:
        def execute(self, _stmt):
            return queue.pop(0)

    monkeypatch.setattr(liq, "build_grid_rows", lambda *_a, **_k: [])
    import app.services.novedades.bonos_import as bi

    monkeypatch.setattr(bi, "load_bonos_snapshot", lambda *_a, **_k: ([], {2: {"CMG|DEA|S|H": 3}}))
    monkeypatch.setattr(bi, "load_practicas_snapshot", lambda *_a, **_k: {})
    monkeypatch.setattr(bi, "load_internaciones_snapshot", lambda *_a, **_k: {})
    monkeypatch.setattr(liq, "load_tarifas_by_opcion_key", lambda *_a, **_k: {"CMG|DEA|S|H": 1000})
    # 3*1000=3000 → concepto 90

    result = liq.build_liquidacion_rows(DB(), periodo_id=1)
    assert len(result) == 1
    assert result[0].concepto == 90
    assert result[0].empresa == "CMG"
    assert result[0].monto == Decimal("3000")


def test_no_cargas_no_special_omitted(monkeypatch):
    periodo = SimpleNamespace(id=1, estado=PeriodoEstado.closed, deleted_at=None)
    prof = SimpleNamespace(id=3, legajo="3", full_name="X", deleted_at=None)
    queue = [
        FakeResult(periodo),
        FakeResult([]),  # ajustes
        FakeResult([prof]),
    ]

    class DB:
        def execute(self, _stmt):
            return queue.pop(0)

    monkeypatch.setattr(liq, "build_grid_rows", lambda *_a, **_k: [])
    import app.services.novedades.bonos_import as bi

    monkeypatch.setattr(bi, "load_bonos_snapshot", lambda *_a, **_k: ([], {3: {"CMG|GUA|S|H": 10}}))
    monkeypatch.setattr(bi, "load_practicas_snapshot", lambda *_a, **_k: {})
    monkeypatch.setattr(bi, "load_internaciones_snapshot", lambda *_a, **_k: {})
    monkeypatch.setattr(liq, "load_tarifas_by_opcion_key", lambda *_a, **_k: {"CMG|GUA|S|H": 100})

    result = liq.build_liquidacion_rows(DB(), periodo_id=1)
    assert result == []


def test_ajustes_prorrateo(monkeypatch):
    periodo = SimpleNamespace(id=1, estado=PeriodoEstado.closed, deleted_at=None)
    svc50 = SimpleNamespace(id=10, nombre="S50", concepto_liquidacion=50)
    svc150 = SimpleNamespace(id=11, nombre="S150", concepto_liquidacion=150)
    rows = [
        SimpleNamespace(professional_id=1, servicio_id=10, valor=Decimal("0"), tipo="hora_extra"),
        SimpleNamespace(professional_id=1, servicio_id=11, valor=Decimal("0"), tipo="hora_extra"),
    ]
    prof = SimpleNamespace(id=1, legajo="9", full_name="P", deleted_at=None)
    ajuste = SimpleNamespace(professional_id=1, importe=Decimal("200"), deleted_at=None, servicio_id=None)
    queue = [
        FakeResult(periodo),
        FakeResult([svc50, svc150]),
        FakeResult([ajuste]),
        FakeResult([prof]),
    ]

    class DB:
        def execute(self, _stmt):
            return queue.pop(0)

    monkeypatch.setattr(liq, "build_grid_rows", lambda *_a, **_k: rows)
    import app.services.novedades.bonos_import as bi

    monkeypatch.setattr(bi, "load_bonos_snapshot", lambda *_a, **_k: ([], {}))
    monkeypatch.setattr(bi, "load_practicas_snapshot", lambda *_a, **_k: {})
    monkeypatch.setattr(bi, "load_internaciones_snapshot", lambda *_a, **_k: {})
    monkeypatch.setattr(liq, "load_tarifas_by_opcion_key", lambda *_a, **_k: {})

    result = liq.build_liquidacion_rows(DB(), periodo_id=1)
    by_c = {r.concepto: r for r in result}
    assert by_c[50].monto == Decimal("100")
    assert by_c[150].monto == Decimal("100")
    assert by_c[50].empresa == "CMG"
    assert by_c[150].empresa == "CHI"


def test_ajuste_con_servicio_va_al_concepto(monkeypatch):
    periodo = SimpleNamespace(id=1, estado=PeriodoEstado.closed, deleted_at=None)
    svc50 = SimpleNamespace(id=10, nombre="S50", concepto_liquidacion=50)
    svc150 = SimpleNamespace(id=11, nombre="S150", concepto_liquidacion=150)
    rows = [
        SimpleNamespace(professional_id=1, servicio_id=10, valor=Decimal("0"), tipo="hora_extra"),
        SimpleNamespace(professional_id=1, servicio_id=11, valor=Decimal("0"), tipo="hora_extra"),
    ]
    prof = SimpleNamespace(id=1, legajo="9", full_name="P", deleted_at=None)
    ajuste = SimpleNamespace(
        professional_id=1, importe=Decimal("-500"), deleted_at=None, servicio_id=10
    )
    queue = [
        FakeResult(periodo),
        FakeResult([svc50, svc150]),
        FakeResult([ajuste]),
        FakeResult([prof]),
    ]

    class DB:
        def execute(self, _stmt):
            return queue.pop(0)

    monkeypatch.setattr(liq, "build_grid_rows", lambda *_a, **_k: rows)
    import app.services.novedades.bonos_import as bi

    monkeypatch.setattr(bi, "load_bonos_snapshot", lambda *_a, **_k: ([], {}))
    monkeypatch.setattr(bi, "load_practicas_snapshot", lambda *_a, **_k: {})
    monkeypatch.setattr(bi, "load_internaciones_snapshot", lambda *_a, **_k: {})
    monkeypatch.setattr(liq, "load_tarifas_by_opcion_key", lambda *_a, **_k: {})

    result = liq.build_liquidacion_rows(DB(), periodo_id=1)
    by_c = {r.concepto: r for r in result}
    assert by_c[50].monto == Decimal("-500")
    assert 150 not in by_c


def test_export_xlsx_headers(monkeypatch):
    monkeypatch.setattr(
        liq,
        "build_liquidacion_rows",
        lambda *_a, **_k: [liq.LiquidacionRow(empresa="CMG", legajo="1", monto=Decimal("10.5"), concepto=50)],
    )
    content = liq.export_liquidacion_xlsx_bytes(SimpleNamespace(), periodo_id=1)
    assert content[:2] == b"PK"  # zip/xlsx
