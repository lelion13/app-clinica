from datetime import time
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.services.distribucion import agenda_ocupacion as agenda_svc
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


def _ocup_row(
    *,
    dia="jueves",
    hora_desde="09:00:00",
    hora_hasta="13:00:00",
    id_agenda=10,
    medico="DOC",
    especialidad="CARDIO",
    especialidad_agenda=None,
    medico_col=None,
):
    # 2026-08-06 is Thursday → JS weekday 4, Python weekday 3
    return SimpleNamespace(
        id=1,
        id_dato="d1",
        tipo="SEDE",
        especialidad_agenda=especialidad_agenda if especialidad_agenda is not None else especialidad,
        medico=medico_col if medico_col is not None else medico,
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
    rooms = [_room()]
    hours = [_hour(1, 4, "08:00:00", "12:00:00")]
    monkeypatch.setattr(service.room_agenda_map_service, "agenda_to_room_map", lambda _db: {})
    result = service.compute_indicadores(FakeDB(rooms, hours, []), date_str="2026-08-06")
    assert result.enabled_hours == 4.0
    assert result.occupied_hours == 0.0
    assert result.occupancy_percent == 0.0
    assert result.rooms_without_agenda == 1
    assert result.period == "day"
    assert result.date == "2026-08-06"


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


def test_especialidad_filter_ignores_especialidad_agenda(monkeypatch):
    rooms = [_room()]
    hours = [_hour(1, 4, "08:00:00", "12:00:00")]
    row = _ocup_row(
        especialidad="CARDIO",
        especialidad_agenda="TRAUMA",
        hora_desde="09:00:00",
        hora_hasta="10:00:00",
    )
    monkeypatch.setattr(service.room_agenda_map_service, "agenda_to_room_map", lambda _db: {10: 1})
    by_agenda = service.compute_indicadores(
        FakeDB(rooms, hours, [row]), date_str="2026-08-06", especialidad="TRAUMA"
    )
    by_payload = service.compute_indicadores(
        FakeDB(rooms, hours, [row]), date_str="2026-08-06", especialidad="CARDIO"
    )
    assert by_agenda.occupied_hours == 0.0
    assert by_payload.occupied_hours == 1.0


def test_tops_and_empty_labels(monkeypatch):
    rooms = [_room()]
    hours = [_hour(1, 4, "08:00:00", "12:00:00")]
    a = _ocup_row(id_agenda=10, especialidad="CARDIO", medico="DOC", hora_desde="09:00:00", hora_hasta="10:00:00")
    b = _ocup_row(id_agenda=11, especialidad="", medico="", hora_desde="10:00:00", hora_hasta="11:00:00")
    b.id = 2
    b.payload = {**b.payload, "id_agenda": 11, "especialidad": "", "medico": ""}
    monkeypatch.setattr(service.room_agenda_map_service, "agenda_to_room_map", lambda _db: {10: 1, 11: 1})
    result = service.compute_indicadores(FakeDB(rooms, hours, [a, b]), date_str="2026-08-06")
    assert result.occupied_hours == 2.0
    labels_esp = {t.label: t for t in result.top_especialidad}
    assert "CARDIO" in labels_esp
    assert "Sin especialidad" in labels_esp
    assert labels_esp["CARDIO"].hours == 1.0
    assert labels_esp["CARDIO"].percent_box == 25.0
    assert labels_esp["CARDIO"].percent_occupied == 50.0
    labels_med = {t.label for t in result.top_medico}
    assert "DOC" in labels_med
    assert "Sin médico" in labels_med


def test_month_sums_weekdays(monkeypatch):
    # August 2026: Thursdays = 6, 13, 20, 27 → 4 Thursdays (JS weekday 4)
    rooms = [_room()]
    hours = [_hour(1, 4, "08:00:00", "12:00:00")]  # 4h each Thursday
    row = _ocup_row(hora_desde="09:00:00", hora_hasta="10:00:00")  # 1h per Thursday occurrence
    monkeypatch.setattr(service.room_agenda_map_service, "agenda_to_room_map", lambda _db: {10: 1})
    result = service.compute_indicadores(
        FakeDB(rooms, hours, [row]), period="month", month_str="2026-08"
    )
    assert result.period == "month"
    assert result.month == "2026-08"
    assert result.date is None
    assert result.enabled_hours == 16.0  # 4 Thursdays * 4h
    assert result.occupied_hours == 4.0  # 4 Thursdays * 1h
    assert result.occupancy_percent == 25.0


def test_invalid_date():
    with pytest.raises(HTTPException) as exc:
        service.compute_indicadores(FakeDB([], [], []), date_str="nope")
    assert exc.value.status_code == 422


def test_filter_options_payload_only():
    row = SimpleNamespace(
        id=1,
        id_dato="d1",
        tipo="T",
        especialidad_agenda="FROM_AGENDA",
        medico="FROM_COL",
        fecha_hasta="2026-12-31",
        payload={
            "id_dominio": 1,
            "tipo": "T",
            "especialidad": "FROM_PAYLOAD",
            "medico": "MED_PAYLOAD",
            "dia": "lunes",
        },
    )
    db = FakeDB([], [], [row])
    opts = agenda_svc.list_filter_options(db)
    esp_values = {o.value for o in opts.especialidad}
    med_values = {o.value for o in opts.medico}
    assert "FROM_PAYLOAD" in esp_values
    assert "FROM_AGENDA" not in esp_values
    assert "MED_PAYLOAD" in med_values
    assert "FROM_COL" not in med_values
