from datetime import date, time
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.services.distribucion import indicadores_ocupacion as service


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
    def __init__(self, rooms, hours, ocupacion):
        self.rooms = rooms
        self.hours = hours
        self.ocupacion = ocupacion

    def execute(self, statement):
        sql = str(statement).lower()
        if "room_operating_hours" in sql or "roomoperatinghour" in sql:
            return FakeResult(self.hours)
        if "ocupacion" in sql or "ocupacionhorarioactivo" in sql:
            return FakeResult(self.ocupacion)
        return FakeResult(self.rooms)


def _room(rid=1, code="401", location_id=1):
    return SimpleNamespace(id=rid, code=code, location_id=location_id, deleted_at=None)


def _hour(room_id, weekday, start="08:00:00", end="12:00:00"):
    sh, sm, *_ = [int(x) for x in start.split(":")]
    eh, em, *_ = [int(x) for x in end.split(":")]
    return SimpleNamespace(
        room_id=room_id,
        weekday=weekday,
        start_time=time(sh, sm),
        end_time=time(eh, em),
        deleted_at=None,
    )


def _ocup_row(*, dia="jueves", hora_desde="09:00:00", hora_hasta="13:00:00", id_agenda=10, medico="DOC", especialidad="CARDIO"):
    # 2026-08-06 is Thursday → JS weekday 4, Python weekday 3
    return SimpleNamespace(
        id=1,
        id_dato="d1",
        tipo="SEDE",
        especialidad_agenda=especialidad,
        medico=medico,
        fecha_hasta="2026-12-31",
        payload={
            "id_agenda": id_agenda,
            "dia": dia,
            "fecha_desde": "2026-01-01",
            "fecha_hasta": "2026-12-31",
            "hora_desde": hora_desde,
            "hora_hasta": hora_hasta,
            "especialidad": especialidad,
            "medico": medico,
        },
    )


def test_hours_between():
    assert service._hours_between(time(8, 0), time(12, 0)) == 4.0
    assert service._hours_between(time(12, 0), time(8, 0)) == 0.0


def test_room_without_agenda_zero_occupied(monkeypatch):
    # Thursday 2026-08-06 → JS weekday 4
    rooms = [_room()]
    hours = [_hour(1, 4, "08:00:00", "12:00:00")]
    monkeypatch.setattr(service.room_agenda_map_service, "agenda_to_room_map", lambda _db: {})
    result = service.compute_indicadores(FakeDB(rooms, hours, []), date_str="2026-08-06")
    assert result.enabled_hours == 4.0
    assert result.occupied_hours == 0.0
    assert result.occupancy_percent == 0.0
    assert result.rooms_without_agenda == 1


def test_room_without_hours_listed(monkeypatch):
    rooms = [_room()]
    monkeypatch.setattr(service.room_agenda_map_service, "agenda_to_room_map", lambda _db: {10: 1})
    result = service.compute_indicadores(FakeDB(rooms, [], []), date_str="2026-08-06")
    assert result.enabled_hours == 0.0
    assert result.occupancy_percent is None
    assert len(result.rooms_without_hours) == 1
    assert result.rooms_without_hours[0].code == "401"


def test_percent_can_exceed_100(monkeypatch):
    rooms = [_room()]
    hours = [_hour(1, 4, "08:00:00", "11:00:00")]  # 3h enabled
    row = _ocup_row(hora_desde="09:00:00", hora_hasta="13:00:00")  # 4h sync
    monkeypatch.setattr(service.room_agenda_map_service, "agenda_to_room_map", lambda _db: {10: 1})
    result = service.compute_indicadores(FakeDB(rooms, hours, [row]), date_str="2026-08-06")
    assert result.enabled_hours == 3.0
    assert result.occupied_hours == 4.0
    assert result.occupancy_percent == pytest.approx(133.33, abs=0.02)
    assert result.free_hours == 0.0


def test_medico_filter_does_not_reduce_enabled(monkeypatch):
    rooms = [_room()]
    hours = [_hour(1, 4, "08:00:00", "12:00:00")]
    a = _ocup_row(id_agenda=10, medico="APECECHEA", hora_desde="09:00:00", hora_hasta="10:00:00")
    b = _ocup_row(id_agenda=11, medico="OTRO", hora_desde="10:00:00", hora_hasta="11:00:00")
    # both map to same room — need two agendas; FakeDB one row id ok
    b.id = 2
    b.payload = {**b.payload, "id_agenda": 11}
    monkeypatch.setattr(service.room_agenda_map_service, "agenda_to_room_map", lambda _db: {10: 1, 11: 1})
    full = service.compute_indicadores(FakeDB(rooms, hours, [a, b]), date_str="2026-08-06")
    filtered = service.compute_indicadores(
        FakeDB(rooms, hours, [a, b]), date_str="2026-08-06", medico="APECECHEA"
    )
    assert full.enabled_hours == filtered.enabled_hours == 4.0
    assert full.occupied_hours == 2.0
    assert filtered.occupied_hours == 1.0


def test_invalid_date():
    with pytest.raises(HTTPException) as exc:
        service.compute_indicadores(FakeDB([], [], []), date_str="nope")
    assert exc.value.status_code == 422
