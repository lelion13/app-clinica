import pytest
from fastapi import HTTPException

from app.services.distribucion import turnos_resumen as service


def test_fetch_requires_config(monkeypatch):
    monkeypatch.setattr(service.settings, "distribucion_turnos_resumen_url", "")
    monkeypatch.setattr(service.settings, "novedades_prof_sync_token", "tok")
    with pytest.raises(HTTPException) as exc:
        service.fetch_turnos_resumen(fecha_desde="2026-10-01", fecha_hasta="2026-10-01")
    assert exc.value.status_code == 422


def test_fetch_rejects_inverted_range():
    with pytest.raises(HTTPException) as exc:
        service.fetch_turnos_resumen(fecha_desde="2026-10-31", fecha_hasta="2026-10-01")
    assert exc.value.status_code == 422


def test_fetch_ok_array_root(monkeypatch):
    """El API real responde un array de filas (no wrapper con detalle)."""
    monkeypatch.setattr(
        service.settings,
        "distribucion_turnos_resumen_url",
        "https://example.test/is/turnos/resumen",
    )
    monkeypatch.setattr(service.settings, "novedades_prof_sync_token", "secret-token")

    captured = {}

    class FakeResponse:
        status_code = 200

        def json(self):
            return [
                {
                    "turno_horario_id": 10,
                    "total_turnos": 10,
                    "atendidos": 2,
                    "ausentes": 3,
                    "cancelados": 1,
                    "espera_promedio_dias": 2,
                },
                {
                    "turno_horario_id": 20,
                    "total_turnos": 30,
                    "atendidos": 6,
                    "ausentes": 4,
                    "cancelados": 2,
                    "espera_promedio_dias": 4,
                },
            ]

    class FakeClient:
        def __init__(self, *args, **kwargs):
            captured["timeout"] = kwargs.get("timeout")

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def get(self, url, params=None, headers=None):
            captured["url"] = url
            captured["params"] = params
            captured["headers"] = headers
            return FakeResponse()

    monkeypatch.setattr(service.httpx, "Client", FakeClient)
    result = service.fetch_turnos_resumen(fecha_desde="2026-10-01", fecha_hasta="2026-10-31")

    assert captured["params"] == {"fecha_desde": "2026-10-01", "fecha_hasta": "2026-10-31"}
    assert captured["headers"]["Authorization"] == "Bearer secret-token"
    assert result.total_turnos == 40
    assert len(result.detalle) == 2
    assert result.detalle[0].turno_horario_id == 10
    assert result.detalle[1].atendidos == 6
    assert result.detalle[0].ausentes == 3


def test_fetch_ok_wrapped_detalle(monkeypatch):
    monkeypatch.setattr(
        service.settings,
        "distribucion_turnos_resumen_url",
        "https://example.test/is/turnos/resumen",
    )
    monkeypatch.setattr(service.settings, "novedades_prof_sync_token", "secret-token")

    class FakeResponse:
        status_code = 200

        def json(self):
            return {
                "fecha_desde": "2026-10-01",
                "fecha_hasta": "2026-10-31",
                "total_turnos": 5,
                "detalle": [{"turno_horario_id": 1, "total_turnos": 5, "presentes": 2}],
            }

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def get(self, *args, **kwargs):
            return FakeResponse()

    monkeypatch.setattr(service.httpx, "Client", FakeClient)
    result = service.fetch_turnos_resumen(fecha_desde="2026-10-01", fecha_hasta="2026-10-31")
    assert result.fecha_desde == "2026-10-01"
    assert result.total_turnos == 5
    assert result.detalle[0].presentes == 2


def test_fetch_upstream_error_hides_token(monkeypatch):
    monkeypatch.setattr(
        service.settings,
        "distribucion_turnos_resumen_url",
        "https://example.test/is/turnos/resumen",
    )
    monkeypatch.setattr(service.settings, "novedades_prof_sync_token", "secret-token")

    class BoomClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def get(self, *args, **kwargs):
            raise RuntimeError("connection refused")

    monkeypatch.setattr(service.httpx, "Client", BoomClient)
    with pytest.raises(HTTPException) as exc:
        service.fetch_turnos_resumen(fecha_desde="2026-10-01", fecha_hasta="2026-10-01")
    assert exc.value.status_code == 502
    assert "secret-token" not in str(exc.value.detail)


def test_fetch_upstream_http_status(monkeypatch):
    monkeypatch.setattr(
        service.settings,
        "distribucion_turnos_resumen_url",
        "https://example.test/is/turnos/resumen",
    )
    monkeypatch.setattr(service.settings, "novedades_prof_sync_token", "secret-token")

    class FakeResponse:
        status_code = 403

        def json(self):
            return {"error": "forbidden"}

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def get(self, *args, **kwargs):
            return FakeResponse()

    monkeypatch.setattr(service.httpx, "Client", FakeClient)
    with pytest.raises(HTTPException) as exc:
        service.fetch_turnos_resumen(fecha_desde="2026-10-01", fecha_hasta="2026-10-01")
    assert exc.value.status_code == 502
    assert "HTTP 403" in str(exc.value.detail)
    assert "secret-token" not in str(exc.value.detail)


def test_fetch_invalid_date():
    with pytest.raises(HTTPException) as exc:
        service.fetch_turnos_resumen(fecha_desde="nope", fecha_hasta="2026-10-01")
    assert exc.value.status_code == 422


def test_fetch_ok_null_pct_fields(monkeypatch):
    """Upstream a veces manda null en pct_cancel_*; no debe romper validación."""
    monkeypatch.setattr(
        service.settings,
        "distribucion_turnos_resumen_url",
        "https://example.test/is/turnos/resumen",
    )
    monkeypatch.setattr(service.settings, "novedades_prof_sync_token", "secret-token")

    class FakeResponse:
        status_code = 200

        def json(self):
            return [
                {
                    "turno_horario_id": 146526,
                    "total_turnos": 5,
                    "espera_promedio_dias": 20.6,
                    "asignados": 0,
                    "en_espera": 0,
                    "presentes": 2,
                    "atendidos": 0,
                    "ausentes": 2,
                    "cancelados": 1,
                    "pct_cancelados": 20.0,
                    "pct_cancel_paciente": None,
                    "pct_cancel_otros": None,
                    "pct_ausentismo": 50.0,
                }
            ]

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def get(self, *args, **kwargs):
            return FakeResponse()

    monkeypatch.setattr(service.httpx, "Client", FakeClient)
    result = service.fetch_turnos_resumen(fecha_desde="2026-10-20", fecha_hasta="2026-10-20")
    assert len(result.detalle) == 1
    assert result.detalle[0].pct_cancel_paciente == 0
    assert result.detalle[0].pct_cancel_otros == 0
    assert result.detalle[0].ausentes == 2
