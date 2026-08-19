from datetime import date
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.models.novedades import PeriodoEstado
from app.models.user import UserRole
from app.services.novedades import bonos_import as bonos
from app.services.novedades import capital_humano
from app.services.novedades.capital_humano import has_special_bono_service


def test_normalize_remote_item():
    assert bonos._normalize_remote_item(
        {
            "centro": "CMG",
            "servicio": "CAP",
            "semana": "LUNES_VIERNES",
            "horario": "DIA",
            "profesional": "111",
            "cantidad": 160,
        }
    ) == ("CMG", "CAP", "LUNES_VIERNES", "DIA", "111", 160)


def test_normalize_rejects_incomplete():
    assert bonos._normalize_remote_item({"centro": "CMG", "profesional": "1"}) is None


def test_import_requires_open_period_with_dates(monkeypatch):
    user = SimpleNamespace(id=1, role=UserRole.admin)
    periodo = SimpleNamespace(
        id=1,
        fecha_inicio=None,
        fecha_fin=None,
        estado=PeriodoEstado.open,
        deleted_at=None,
    )

    class DB:
        def execute(self, stmt):
            return SimpleNamespace(scalar_one_or_none=lambda: periodo)

    with pytest.raises(HTTPException) as exc:
        bonos.import_bonos_for_periodo(DB(), 1, user)
    assert exc.value.status_code == 422
    assert "fecha" in exc.value.detail.lower()


def test_import_blocks_closed_period(monkeypatch):
    user = SimpleNamespace(id=1, role=UserRole.admin)
    periodo = SimpleNamespace(
        id=1,
        fecha_inicio=date(2026, 7, 1),
        fecha_fin=date(2026, 7, 31),
        estado=PeriodoEstado.closed,
        deleted_at=None,
    )

    class DB:
        def execute(self, stmt):
            return SimpleNamespace(scalar_one_or_none=lambda: periodo)

    with pytest.raises(HTTPException) as exc:
        bonos.import_bonos_for_periodo(DB(), 1, user)
    assert exc.value.status_code == 422
    assert "cerrado" in exc.value.detail.lower()


def test_import_does_not_mutate_when_fetch_fails(monkeypatch):
    from sqlalchemy.sql.dml import Delete

    user = SimpleNamespace(id=1, role=UserRole.admin)
    periodo = SimpleNamespace(
        id=1,
        fecha_inicio=date(2026, 7, 1),
        fecha_fin=date(2026, 7, 31),
        estado=PeriodoEstado.open,
        deleted_at=None,
    )
    deleted = {"called": False}

    class DB:
        def execute(self, stmt):
            if isinstance(stmt, Delete):
                deleted["called"] = True
            return SimpleNamespace(scalar_one_or_none=lambda: periodo)

        def commit(self):
            raise AssertionError("commit should not run")

    monkeypatch.setattr(
        bonos,
        "_fetch_remote_bonos",
        lambda *a, **k: (_ for _ in ()).throw(HTTPException(status_code=502, detail="down")),
    )
    with pytest.raises(HTTPException) as exc:
        bonos.import_bonos_for_periodo(DB(), 1, user)
    assert exc.value.status_code == 502
    assert deleted["called"] is False


def test_aggregate_sums_duplicates():
    """Unit-level: same key sums via defaultdict logic mirrored from import."""
    from collections import defaultdict

    aggregated = defaultdict(int)
    for cantidad in (10, 20, 5):
        aggregated[(1, "CMG", "CAP", "LUNES_VIERNES", "DIA")] += cantidad
    assert aggregated[(1, "CMG", "CAP", "LUNES_VIERNES", "DIA")] == 35


def test_opcion_key_label():
    assert bonos.opcion_key("CMG", "CAP", "LUNES_VIERNES", "DIA") == "CMG|CAP|LUNES_VIERNES|DIA"
    assert "CAP" in bonos.opcion_label("CMG", "CAP", "LUNES_VIERNES", "DIA")


def test_has_special_bono_service_true():
    bonos_map = {"CMG|CAP|LUNES_VIERNES|DIA": 3}
    assert has_special_bono_service(bonos_map) is True


def test_has_special_bono_service_false_for_other_services():
    bonos_map = {"CMG|CLINICA|LUNES_VIERNES|DIA": 5}
    assert has_special_bono_service(bonos_map) is False


def test_has_special_bono_service_exact_match_only():
    bonos_map = {"CMG|cap|LUNES_VIERNES|DIA": 2, "CMG|CAP PED|LUNES_VIERNES|DIA": 1}
    assert has_special_bono_service(bonos_map) is False


def test_build_capital_rows_promotes_special_bonus_only(monkeypatch):
    monkeypatch.setattr(capital_humano, "build_grid_rows", lambda *a, **k: [])
    monkeypatch.setattr(
        bonos,
        "load_bonos_snapshot",
        lambda *a, **k: (
            [],
            {
                1: {"CMG|CAP|LUNES_VIERNES|DIA": 4},
                2: {"CMG|CLINICA|LUNES_VIERNES|DIA": 9},
            },
        ),
    )

    prof_special = SimpleNamespace(id=1, full_name="Prof CAP", legajo="1", codprof="001", deleted_at=None)

    class _ScalarResult:
        def __init__(self, items):
            self._items = items

        def scalars(self):
            return self

        def all(self):
            return self._items

    class DB:
        def __init__(self):
            self._calls = 0

        def execute(self, _stmt):
            self._calls += 1
            if self._calls == 1:
                return _ScalarResult([])  # ajustes
            return _ScalarResult([prof_special])  # professionals lookup

    rows = capital_humano.build_capital_humano_rows(DB(), periodo_id=1, include_bonos=True)
    assert len(rows) == 1
    assert rows[0].professional_name == "Prof CAP"
    assert rows[0].monto_total == 0


def test_list_solo_bonos_excludes_promoted_special(monkeypatch):
    monkeypatch.setattr(
        bonos,
        "load_bonos_snapshot",
        lambda *a, **k: (
            [],
            {
                1: {"CMG|DEA|LUNES_VIERNES|DIA": 3},
                2: {"CMG|CLINICA|LUNES_VIERNES|DIA": 2},
            },
        ),
    )
    monkeypatch.setattr(
        capital_humano,
        "build_capital_humano_rows",
        lambda *a, **k: [SimpleNamespace(professional_id=1)],
    )

    prof_other = SimpleNamespace(id=2, full_name="Prof Clinica", legajo="2", codprof="002", deleted_at=None)

    class _ScalarResult:
        def __init__(self, items):
            self._items = items

        def scalars(self):
            return self

        def all(self):
            return self._items

    class DB:
        def execute(self, _stmt):
            return _ScalarResult([prof_other])

    rows = bonos.list_solo_bonos(DB(), periodo_id=1)
    assert len(rows) == 1
    assert rows[0].professional_id == 2
