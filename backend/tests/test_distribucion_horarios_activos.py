from datetime import date, datetime
from types import SimpleNamespace
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
            "id_agenda": 10366,
            "nombre_agenda": "ART - TRAUMATOLOGIA - APECECHEA CAIRONE DIEGO",
            "especialidad": "TRAUMATOLOGIA Y ORTOPEDIA ",
            "dia": "lunes",
            "fecha_desde": "2023-01-01",
            "hora_desde": "8:00:00",
            "fecha_hasta": "2024-12-31",
            "hora_hasta": "12:00:00",
            "duracion_turno": 10,
            "cantidad_turnos": 24.0,
            "cantidad_sobreturno": 2,
            "consultorio": "CONSULTORIO 1",
        }
    )
    assert item.id == 62644
    assert item.id_dato == "62644-2023-10-07"
    assert item.id_agenda == 10366
    assert item.id_dominio == 1651
    assert item.tipo == "ART"
    assert item.especialidad_agenda == "TRAUMATOLOGIA"
    assert item.medico == "APECECHEA CAIRONE DIEGO"
    assert item.especialidad == "TRAUMATOLOGIA Y ORTOPEDIA"
    assert item.dia == "lunes"
    assert item.cantidad_turnos == 24.0
    assert item.cantidad_sobreturno == 2


def test_fetch_requires_config(monkeypatch):
    monkeypatch.setattr(service.settings, "distribucion_horarios_activos_url", "")
    monkeypatch.setattr(service.settings, "novedades_prof_sync_token", "tok")
    with pytest.raises(HTTPException) as exc:
        service._fetch_remote_rows()
    assert exc.value.status_code == 422


class FakeDB:
    def __init__(self):
        self.deleted = False
        self.added = []
        self.committed = False
        self.rolled_back = False
        self._rows = []

    def execute(self, stmt):
        # delete or select — both ok for this fake
        self.deleted = True
        return SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: self._rows))

    def add_all(self, items):
        self.added = list(items)

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


def test_sync_wipe_reload(monkeypatch):
    monkeypatch.setattr(
        service,
        "_fetch_remote_rows",
        lambda: [
            {
                "id": 1,
                "id_dato": "1-a",
                "id_dominio": 10,
                "id_agenda": 100,
                "nombre_agenda": "X - Y - Z",
                "especialidad": "CARDIO",
                "dia": "martes",
                "fecha_desde": "2024-01-01",
                "hora_desde": "9:00:00",
                "fecha_hasta": "2099-12-31",
                "hora_hasta": "12:00:00",
                "duracion_turno": 15,
                "cantidad_turnos": 12,
                "cantidad_sobreturno": 1,
            },
            {
                "id": 2,
                "id_dato": None,
                "especialidad": "SKIP",
            },
        ],
    )
    db = FakeDB()
    result = service.sync_horarios_activos(db)
    assert result.synced == 1
    assert result.skipped == 1
    assert db.deleted is True
    assert len(db.added) == 1
    assert db.added[0].id_dato == "1-a"
    assert db.added[0].tipo == "X"
    assert db.committed is True


def test_sync_does_not_touch_db_when_fetch_fails(monkeypatch):
    def boom():
        raise HTTPException(status_code=502, detail="down")

    monkeypatch.setattr(service, "_fetch_remote_rows", boom)
    db = FakeDB()
    with pytest.raises(HTTPException) as exc:
        service.sync_horarios_activos(db)
    assert exc.value.status_code == 502
    assert db.committed is False
    assert db.added == []


def test_list_filters_fecha_hasta(monkeypatch):
    monkeypatch.setattr(service, "_business_today", lambda: date(2026, 8, 3))
    row_ok = SimpleNamespace(
        id_dato="1",
        horario_id=1,
        id_agenda=1,
        id_dominio=1,
        tipo="A",
        especialidad_agenda="B",
        medico="C",
        especialidad="ESP",
        dia="lunes",
        fecha_desde="2024-01-01",
        hora_desde="8:00:00",
        fecha_hasta="2099-01-01",
        hora_hasta="12:00:00",
        duracion_turno=10,
        cantidad_turnos=5,
        cantidad_sobreturno=0,
    )
    row_old = SimpleNamespace(
        id_dato="2",
        horario_id=2,
        id_agenda=2,
        id_dominio=2,
        tipo=None,
        especialidad_agenda=None,
        medico=None,
        especialidad="OLD",
        dia="martes",
        fecha_desde="2020-01-01",
        hora_desde="8:00:00",
        fecha_hasta="2020-01-01",
        hora_hasta="12:00:00",
        duracion_turno=10,
        cantidad_turnos=5,
        cantidad_sobreturno=0,
    )
    db = FakeDB()
    db._rows = [row_ok, row_old]
    result = service.list_horarios_activos(db)
    assert len(result.items) == 1
    assert result.items[0].id_dato == "1"


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
        service._fetch_remote_rows()
    assert exc.value.status_code == 502
    assert "secret" not in str(exc.value.detail)
