from datetime import date
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.services.distribucion import horarios_activos as service


def test_split_nombre_agenda_three_parts():
    assert service._split_nombre_agenda("ART - TRAUMATOLOGIA - APECECHEA CAIRONE DIEGO") == (
        "ART",
        "TRAUMATOLOGIA",
        "APECECHEA CAIRONE DIEGO",
    )


def test_split_nombre_agenda_more_than_three():
    assert service._split_nombre_agenda("A - B - C - D") == ("A", "B", "C - D")


def test_split_nombre_agenda_fewer_parts():
    assert service._split_nombre_agenda("SOLO") == ("SOLO", None, None)
    assert service._split_nombre_agenda("A - B") == ("A", "B", None)
    assert service._split_nombre_agenda(None) == (None, None, None)
    assert service._split_nombre_agenda("") == (None, None, None)


def test_fecha_hasta_vigente():
    today = date(2026, 8, 3)
    assert service._fecha_hasta_vigente("2026-08-03", today=today) is True
    assert service._fecha_hasta_vigente("2026-12-31", today=today) is True
    assert service._fecha_hasta_vigente("2026-08-02", today=today) is False
    assert service._fecha_hasta_vigente("2024-12-31 12:00:00", today=today) is False
    assert service._fecha_hasta_vigente(None, today=today) is False
    assert service._fecha_hasta_vigente("no-fecha", today=today) is False


def test_map_row_subset():
    item = service._map_row(
        {
            "id": 62644,
            "id_dato": "62644-2023-10-07",
            "id_dominio": 1651,
            "nombre_agenda": "ART - TRAUMATOLOGIA - APECECHEA CAIRONE DIEGO",
            "especialidad": "TRAUMATOLOGIA Y ORTOPEDIA ",
            "dia": "lunes",
            "fecha_desde": "2023-01-01",
            "hora_desde": "8:00:00",
            "fecha_hasta": "2024-12-31",
            "hora_hasta": "12:00:00",
            "duracion_turno": 10,
            "consultorio": "CONSULTORIO 1",
        }
    )
    assert item.id == 62644
    assert item.id_dato == "62644-2023-10-07"
    assert item.id_dominio == 1651
    assert item.tipo == "ART"
    assert item.especialidad_agenda == "TRAUMATOLOGIA"
    assert item.medico == "APECECHEA CAIRONE DIEGO"
    assert item.especialidad == "TRAUMATOLOGIA Y ORTOPEDIA"
    assert item.dia == "lunes"
    assert item.fecha_desde == "2023-01-01"
    assert item.hora_desde == "8:00:00"
    assert item.fecha_hasta == "2024-12-31"
    assert item.hora_hasta == "12:00:00"
    assert item.duracion_turno == 10


def test_fetch_requires_config(monkeypatch):
    monkeypatch.setattr(service.settings, "distribucion_horarios_activos_url", "")
    monkeypatch.setattr(service.settings, "novedades_prof_sync_token", "tok")
    with pytest.raises(HTTPException) as exc:
        service.fetch_horarios_activos()
    assert exc.value.status_code == 422


def test_fetch_happy_path(monkeypatch):
    monkeypatch.setattr(
        service.settings,
        "distribucion_horarios_activos_url",
        "https://example.test/is/horarios-activos",
    )
    monkeypatch.setattr(service.settings, "novedades_prof_sync_token", "secret")
    monkeypatch.setattr(service.settings, "distribucion_horarios_activos_timeout", 5.0)

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = [
        {
            "id": 1,
            "id_dato": "1-a",
            "id_dominio": 10,
            "especialidad": "CARDIO",
            "dia": "martes",
            "fecha_desde": "2024-01-01",
            "hora_desde": "9:00:00",
            "fecha_hasta": "2099-12-31",
            "hora_hasta": "12:00:00",
            "duracion_turno": 15,
        },
        {
            "id": 2,
            "id_dato": "2-b",
            "id_dominio": 11,
            "especialidad": "OLD",
            "dia": "lunes",
            "fecha_desde": "2020-01-01",
            "hora_desde": "9:00:00",
            "fecha_hasta": "2020-12-31",
            "hora_hasta": "12:00:00",
            "duracion_turno": 15,
        },
        {
            "id": 3,
            "id_dato": "3-c",
            "id_dominio": 12,
            "especialidad": "NO-DATE",
            "fecha_hasta": None,
        },
    ]

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def get(self, url, headers=None):
            assert "Bearer secret" in (headers or {}).get("Authorization", "")
            assert "horarios-activos" in url
            return mock_response

    monkeypatch.setattr(service.httpx, "Client", FakeClient)
    monkeypatch.setattr(service, "_business_today", lambda: date(2026, 8, 3))
    result = service.fetch_horarios_activos()
    assert len(result.items) == 1
    assert result.items[0].especialidad == "CARDIO"
    assert result.items[0].dia == "martes"
    assert result.items[0].id_dominio == 10


def test_fetch_upstream_error(monkeypatch):
    monkeypatch.setattr(
        service.settings,
        "distribucion_horarios_activos_url",
        "https://example.test/is/horarios-activos",
    )
    monkeypatch.setattr(service.settings, "novedades_prof_sync_token", "secret")

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
        service.fetch_horarios_activos()
    assert exc.value.status_code == 502
    assert "secret" not in str(exc.value.detail)
