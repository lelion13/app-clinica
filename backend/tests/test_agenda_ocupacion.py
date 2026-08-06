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
    id_agenda=None,
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
    if id_agenda is not None:
        payload["id_agenda"] = id_agenda
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
    db = FakeDB(
        [row],
        locations=[SimpleNamespace(id_dominio=1651, name="Sede Centro", tipo="ART", deleted_at=None)],
    )

    # Bypass sqlalchemy select string checks: force location + ocupacion via patched helpers
    monkeypatch.setattr(service, "_location_labels", lambda _db: {(1651, "art"): "Sede Centro"})

    class DB2:
        def execute(self, _statement):
            return FakeResult([row])

    monkeypatch.setattr(
        service.room_agenda_map_service,
        "agenda_to_room_map",
        lambda _db: {},
    )
    monkeypatch.setattr(service, "_rooms_for_location", lambda _db, _loc: [])
    monkeypatch.setattr(service, "_room_code_map", lambda _db: {})

    result = service.list_agenda_events(DB2(), start="2026-08-03", end="2026-08-10")
    assert len(result.events) == 1
    ev = result.events[0]
    assert ev.start == "2026-08-03T09:00:00"
    assert ev.end == "2026-08-03T12:00:00"
    assert ev.title == "APECECHEA"
    assert ev.resource_id == "unassigned"
    assert ev.extended.location_name == "Sede Centro"
    assert any(r.id == "unassigned" for r in result.resources)


def _stub_map(monkeypatch):
    monkeypatch.setattr(service, "_location_labels", lambda _db: {})
    monkeypatch.setattr(service.room_agenda_map_service, "agenda_to_room_map", lambda _db: {})
    monkeypatch.setattr(service, "_rooms_for_location", lambda _db, _loc: [])
    monkeypatch.setattr(service, "_room_code_map", lambda _db: {})


def test_exclude_without_dia(monkeypatch):
    _stub_map(monkeypatch)
    row = _row(dia=None)

    class DB2:
        def execute(self, _statement):
            return FakeResult([row])

    result = service.list_agenda_events(DB2(), start="2026-08-03", end="2026-08-10")
    assert result.events == []


def test_exclude_outside_fecha_range(monkeypatch):
    _stub_map(monkeypatch)
    row = _row(fecha_desde="2020-01-01", fecha_hasta="2020-12-31")

    class DB2:
        def execute(self, _statement):
            return FakeResult([row])

    result = service.list_agenda_events(DB2(), start="2026-08-03", end="2026-08-10")
    assert result.events == []


def test_filter_especialidad_or_agenda(monkeypatch):
    _stub_map(monkeypatch)
    row = _row(especialidad="AAA", especialidad_agenda="BBB")

    class DB2:
        def execute(self, _statement):
            return FakeResult([row])

    hit = service.list_agenda_events(DB2(), start="2026-08-03", end="2026-08-10", especialidad=["BBB"])
    assert len(hit.events) == 1
    miss = service.list_agenda_events(DB2(), start="2026-08-03", end="2026-08-10", especialidad=["ZZZ"])
    assert miss.events == []


def test_location_fallback_to_number(monkeypatch):
    _stub_map(monkeypatch)
    row = _row(id_dominio=999)

    class DB2:
        def execute(self, _statement):
            return FakeResult([row])

    result = service.list_agenda_events(DB2(), start="2026-08-03", end="2026-08-10")
    assert result.events[0].extended.location_name == "999"


def test_mapped_resource_id(monkeypatch):
    monkeypatch.setattr(service, "_location_labels", lambda _db: {})
    monkeypatch.setattr(service.room_agenda_map_service, "agenda_to_room_map", lambda _db: {55: 7})
    monkeypatch.setattr(
        service,
        "_rooms_for_location",
        lambda _db, _loc: [SimpleNamespace(id=7, code="401", deleted_at=None)],
    )
    monkeypatch.setattr(service, "_room_code_map", lambda _db: {7: "401"})
    row = _row(id_agenda=55)

    class DB2:
        def execute(self, _statement):
            return FakeResult([row])

    result = service.list_agenda_events(DB2(), start="2026-08-03", end="2026-08-10")
    assert result.events[0].resource_id == "7"
    assert result.events[0].extended.room_code == "401"


def test_invalid_window():
    with pytest.raises(HTTPException) as exc:
        service.list_agenda_events(FakeDB([]), start="2026-08-10", end="2026-08-03")
    assert exc.value.status_code == 422


def test_location_filter_matches_dominio_and_tipo(monkeypatch):
    _stub_map(monkeypatch)
    match = _row(row_id=1, tipo="SEDE TORRE", id_dominio=1651)
    other = _row(row_id=2, tipo="SEDE CAÑUELAS", id_dominio=1651)
    loc = SimpleNamespace(id=3, id_dominio=1651, tipo="SEDE TORRE", deleted_at=None)

    class DB2:
        def execute(self, statement):
            sql = str(statement)
            if "locations" in sql.lower() or "Location" in sql:
                result = FakeResult([loc])
                result.scalar_one_or_none = lambda: loc
                return result
            return FakeResult([match, other])

    monkeypatch.setattr(service, "_rooms_for_location", lambda _db, _loc: [])
    result = service.list_agenda_events(DB2(), start="2026-08-03", end="2026-08-10", location_id=3)
    assert len(result.events) == 1
    assert result.events[0].extended.tipo == "SEDE TORRE"


def test_dominio_label_prefers_tipo_pair():
    labels = {(1651, "sede torre"): "Torre", (1651, "sede cañuelas"): "Cañuelas"}
    assert service._dominio_label(1651, "SEDE TORRE", labels) == "Torre"
    assert service._dominio_label(1651, "SEDE CAÑUELAS", labels) == "Cañuelas"
    assert service._dominio_label(999, "X", labels) == "999"


def test_tipo_filter_reduces_unassigned(monkeypatch):
    _stub_map(monkeypatch)
    a = _row(row_id=1, tipo="SEDE TORRE", medico="A")
    b = _row(row_id=2, tipo="SEDE CAÑUELAS", medico="B")

    class DB2:
        def execute(self, _statement):
            return FakeResult([a, b])

    result = service.list_agenda_events(DB2(), start="2026-08-03", end="2026-08-10", tipo=["SEDE TORRE"])
    assert len(result.events) == 1
    assert result.events[0].resource_id == "unassigned"
    assert result.events[0].extended.tipo == "SEDE TORRE"


def test_medico_filter_reduces_unassigned(monkeypatch):
    _stub_map(monkeypatch)
    a = _row(row_id=1, medico="APECECHEA")
    b = _row(row_id=2, medico="OTRO")

    class DB2:
        def execute(self, _statement):
            return FakeResult([a, b])

    result = service.list_agenda_events(DB2(), start="2026-08-03", end="2026-08-10", medico=["APECECHEA"])
    assert len(result.events) == 1
    assert result.events[0].title == "APECECHEA"
