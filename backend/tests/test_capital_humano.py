from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.models.user import UserRole
from app.schemas.novedades import AjusteCapitalCreateRequest
from app.services.novedades import capital_humano as ch


class FakeResult:
    def __init__(self, value):
        self._value = value

    def scalar_one_or_none(self):
        return self._value

    def scalars(self):
        return self

    def all(self):
        return self._value if isinstance(self._value, list) else []


def test_create_ajuste_rejects_zero():
    user = SimpleNamespace(id=1, role=UserRole.admin)
    payload = AjusteCapitalCreateRequest(
        professional_id=1,
        periodo_id=1,
        importe=Decimal("0"),
        comentario="x",
    )
    with pytest.raises(HTTPException) as exc:
        ch.create_ajuste(SimpleNamespace(), payload, user)
    assert exc.value.status_code == 422


def test_create_ajuste_rejects_blank_comment():
    user = SimpleNamespace(id=1, role=UserRole.admin)
    payload = AjusteCapitalCreateRequest(
        professional_id=1,
        periodo_id=1,
        importe=Decimal("10"),
        comentario="   ",
    )
    with pytest.raises(HTTPException) as exc:
        ch.create_ajuste(SimpleNamespace(), payload, user)
    assert exc.value.status_code == 422


def test_build_capital_humano_aggregates(monkeypatch):
    monkeypatch.setattr(
        ch,
        "build_grid_rows",
        lambda *a, **k: [
            SimpleNamespace(professional_id=1, valor=Decimal("100")),
            SimpleNamespace(professional_id=1, valor=Decimal("50")),
            SimpleNamespace(professional_id=2, valor=Decimal("20")),
        ],
    )

    class DB:
        def execute(self, stmt):
            sql = str(stmt)
            if "novedades_ajuste_capital" in sql.lower() or "NovedadesAjusteCapital" in sql:
                return FakeResult(
                    [
                        SimpleNamespace(professional_id=1, importe=Decimal("-10"), deleted_at=None),
                    ]
                )
            return FakeResult(
                [
                    SimpleNamespace(id=1, full_name="Ana", legajo="5100", deleted_at=None),
                    SimpleNamespace(id=2, full_name="Bob", legajo=None, deleted_at=None),
                ]
            )

    rows = ch.build_capital_humano_rows(DB(), periodo_id=1)
    by_id = {r.professional_id: r for r in rows}
    assert by_id[1].monto_cargas == Decimal("150")
    assert by_id[1].monto_ajustes == Decimal("-10")
    assert by_id[1].monto_total == Decimal("140")
    assert by_id[2].monto_total == Decimal("20")
