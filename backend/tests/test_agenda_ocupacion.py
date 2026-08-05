from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.services.distribucion import agenda_ocupacion as service


def _row(
    *,
    row_id=1,
    dia="lunes",
    fecha_desde="2026-01-01",
    fecha_hasta="2026-12-31",
    hora_desde="9:00:00",
    hora_hasta="12:00:00",
    tipo="ART",
    especialidad="TRAUMATOLOGIA",
    especialidad_agenda="TRAUMA",
    medico="APECECHEA",
    id_dominio=1651,
):
    payload = {
        "id_dato": f"d-{row_id}",
        "id_dominio": id_dominio,
        "especialidad": especialidad,
        "dia": dia,
        "fecha_desde": fecha_desde,
        "hora_desde": hora_desde,
        "fecha_hasta": fecha_hasta,
        "hora_hasta": hora_hasta,
    }
    return SimpleNamespace(
        id=row_id,
        payload=payload,
        tipo=tipo,
        especialidad_agenda=especialidad_agenda,
        medico=medico,
        fecha_hasta=fecha_hasta,
        id_dato=payload["id_dato"],
    )


class FakeScalars:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items


class FakeResult:
    def __init__(self, items):
        self._items = items

    def scalars(self):
        return FakeScalars(self._items)


class FakeDB:
    def __init__(self, ocupacion_rows, locations=None):
        self.ocupacion_rows = ocupacion_rows
        self.locations = locations or []

    def execute(self, statement):
        # Rough dispatch: Location queries include deleted_at; ocupacion is the rest.
        sql = str(statement)
        if "locations" in sql.lower() or "Location" in sql:
            return FakeResult(self.locations)
        return FakeResult(self.ocupacion_rows)


def test_weekday_from_dia():
    assert service._weekday_from_dia("lunes") == 0
    assert service._weekday_from_dia("MIÉRCOLES") == 2
    assert service._weekday_from_dia("") is None
    assert service._weekday_from_dia("nodia") is None


def test_materialize_monday_in_window(monkeypatch):
    # 2026-08-03 is Monday
    row = _row()
    db = FakeDB([row], locations=[SimpleNamespace(id_dominio=1651, name="Sede Centro", deleted_at=None)])

    # Bypass sqlalchemy select string checks: force location + ocupacion via patched helpers
    monkeypatch.setattr(service, "_location_labels", lambda _db: {1651: "Sede Centro"})

    class DB2:
        def execute(self, _statement):
            return FakeResult([row])

    result = service.list_agenda_events(DB2(), start="2026-08-03", end="2026-08-10")
    assert len(result.events) == 1
    ev = result.events[0]
    assert ev.start == "2026-08-03T09:00:00"
    assert ev.end == "2026-08-03T12:00:00"
    assert ev.title == "APECECHEA"
    assert ev.extended.location_name == "Sede Centro"


def test_exclude_without_dia(monkeypatch):
    monkeypatch.setattr(service, "_location_labels", lambda _db: {})
    row = _row(dia=None)

    class DB2:
        def execute(self, _statement):
            return FakeResult([row])

    result = service.list_agenda_events(DB2(), start="2026-08-03", end="2026-08-10")
    assert result.events == []


def test_exclude_outside_fecha_range(monkeypatch):
    monkeypatch.setattr(service, "_location_labels", lambda _db: {})
    row = _row(fecha_desde="2020-01-01", fecha_hasta="2020-12-31")

    class DB2:
        def execute(self, _statement):
            return FakeResult([row])

    result = service.list_agenda_events(DB2(), start="2026-08-03", end="2026-08-10")
    assert result.events == []


def test_filter_especialidad_or_agenda(monkeypatch):
    monkeypatch.setattr(service, "_location_labels", lambda _db: {})
    row = _row(especialidad="AAA", especialidad_agenda="BBB")

    class DB2:
        def execute(self, _statement):
            return FakeResult([row])

    hit = service.list_agenda_events(DB2(), start="2026-08-03", end="2026-08-10", especialidad=["BBB"])
    assert len(hit.events) == 1
    miss = service.list_agenda_events(DB2(), start="2026-08-03", end="2026-08-10", especialidad=["ZZZ"])
    assert miss.events == []


def test_location_fallback_to_number(monkeypatch):
    monkeypatch.setattr(service, "_location_labels", lambda _db: {})
    row = _row(id_dominio=999)

    class DB2:
        def execute(self, _statement):
            return FakeResult([row])

    result = service.list_agenda_events(DB2(), start="2026-08-03", end="2026-08-10")
    assert result.events[0].extended.location_name == "999"


def test_invalid_window():
    with pytest.raises(HTTPException) as exc:
        service.list_agenda_events(FakeDB([]), start="2026-08-10", end="2026-08-03")
    assert exc.value.status_code == 422
