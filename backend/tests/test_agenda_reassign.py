"""Tests for agenda reassign (DnD validation)."""

from datetime import time
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.services.distribucion import agenda_reassign as service


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

    def scalar_one_or_none(self):
        return self._items[0] if self._items else None


class FakeDB:
    def __init__(self):
        self.rooms = [
            SimpleNamespace(id=1, code="C1", deleted_at=None),
            SimpleNamespace(id=2, code="C2", deleted_at=None),
        ]
        self.maps = []
        self.hours = []
        self.ocupacion = []
        self.added = []
        self.deleted = []

    def execute(self, statement):
        text = str(statement).lower()
        ent = str(statement)
        if "room_operating_hour" in text or "RoomOperatingHour" in ent:
            return FakeResult(list(self.hours))
        if "consulting_room_id_agenda" in text or "ConsultingRoomIdAgenda" in ent:
            items = list(self.maps)
            try:
                sql = str(statement.compile(compile_kwargs={"literal_binds": True})).lower()
            except Exception:
                sql = text
            import re

            m = re.search(r"id_agenda\s*=\s*(\d+)", sql)
            if m:
                aid = int(m.group(1))
                items = [x for x in self.maps if getattr(x, "id_agenda", None) == aid]
            return FakeResult(items)
        if "ocupacion" in text or "OcupacionHorarioActivo" in ent:
            return FakeResult(list(self.ocupacion))
        if "consulting_room" in text or "ConsultingRoom" in ent:
            return FakeResult(list(self.rooms))
        return FakeResult([])

    def add(self, item):
        self.added.append(item)
        self.maps.append(item)

    def delete(self, item):
        self.deleted.append(item)
        self.maps = [m for m in self.maps if m is not item]

    def commit(self):
        return None

    def rollback(self):
        return None


def _ocup_row(id_agenda, dia, h_desde, h_hasta):
    return SimpleNamespace(
        id=1,
        id_dato="x",
        medico=None,
        tipo=None,
        especialidad_agenda=None,
        fecha_hasta=None,
        payload={
            "id_agenda": id_agenda,
            "dia": dia,
            "hora_desde": h_desde,
            "hora_hasta": h_hasta,
            "fecha_desde": "2026-01-01",
            "fecha_hasta": "2026-12-31",
        },
    )


def _hour(room_id, weekday_js, start, end):
    return SimpleNamespace(
        room_id=room_id,
        weekday=weekday_js,
        start_time=start,
        end_time=end,
        deleted_at=None,
    )


def test_interval_helpers():
    assert service._interval_covered(9 * 60, 11 * 60, [(8 * 60, 12 * 60)])
    assert not service._interval_covered(9 * 60, 13 * 60, [(8 * 60, 12 * 60)])
    assert not service._intervals_overlap(9 * 60, 10 * 60, 10 * 60, 11 * 60)
    assert service._intervals_overlap(9 * 60, 11 * 60, 10 * 60, 12 * 60)


def test_assign_ok(monkeypatch):
    db = FakeDB()
    db.ocupacion = [_ocup_row(100, "lunes", "09:00", "11:00")]
    # lunes py=0 → js=1
    db.hours = [_hour(1, 1, time(8, 0), time(18, 0))]

    monkeypatch.setattr(service.map_svc, "_ensure_room", lambda _db, rid: next(r for r in db.rooms if r.id == rid))

    result = service.reassign_agenda(
        db, id_agenda=100, target_room_id=1, actor_id=1, confirm_move=False
    )
    assert result.room_id == 1
    assert result.room_code == "C1"
    assert len(db.added) == 1


def test_outside_hours(monkeypatch):
    db = FakeDB()
    db.ocupacion = [_ocup_row(100, "lunes", "18:00", "20:00")]
    db.hours = [_hour(1, 1, time(8, 0), time(17, 0))]
    monkeypatch.setattr(service.map_svc, "_ensure_room", lambda _db, rid: next(r for r in db.rooms if r.id == rid))

    with pytest.raises(HTTPException) as exc:
        service.reassign_agenda(db, id_agenda=100, target_room_id=1, actor_id=1)
    assert exc.value.status_code == 422
    assert exc.value.detail["code"] == "validation_failed"
    assert exc.value.detail["conflicts"][0]["type"] == "outside_hours"


def test_overlap(monkeypatch):
    db = FakeDB()
    db.ocupacion = [
        _ocup_row(100, "lunes", "10:00", "12:00"),
        _ocup_row(200, "lunes", "09:00", "11:00"),
    ]
    db.hours = [_hour(1, 1, time(8, 0), time(18, 0))]
    db.maps = [SimpleNamespace(id_agenda=200, room_id=1, updated_at=None, updated_by=None)]
    monkeypatch.setattr(service.map_svc, "_ensure_room", lambda _db, rid: next(r for r in db.rooms if r.id == rid))

    with pytest.raises(HTTPException) as exc:
        service.reassign_agenda(db, id_agenda=100, target_room_id=1, actor_id=1)
    assert exc.value.status_code == 422
    assert exc.value.detail["conflicts"][0]["type"] == "overlap"


def test_multi_weekday_fail(monkeypatch):
    db = FakeDB()
    db.ocupacion = [
        _ocup_row(100, "lunes", "09:00", "11:00"),
        _ocup_row(100, "miercoles", "09:00", "11:00"),
    ]
    # only lunes hours (js=1); miercoles js=3 missing
    db.hours = [_hour(1, 1, time(8, 0), time(18, 0))]
    monkeypatch.setattr(service.map_svc, "_ensure_room", lambda _db, rid: next(r for r in db.rooms if r.id == rid))

    with pytest.raises(HTTPException) as exc:
        service.reassign_agenda(db, id_agenda=100, target_room_id=1, actor_id=1)
    assert any(c["type"] == "outside_hours" for c in exc.value.detail["conflicts"])


def test_confirm_move_required(monkeypatch):
    db = FakeDB()
    db.ocupacion = [_ocup_row(100, "lunes", "09:00", "11:00")]
    db.hours = [_hour(2, 1, time(8, 0), time(18, 0))]
    db.maps = [SimpleNamespace(id_agenda=100, room_id=1, updated_at=None, updated_by=None)]
    monkeypatch.setattr(service.map_svc, "_ensure_room", lambda _db, rid: next(r for r in db.rooms if r.id == rid))

    with pytest.raises(HTTPException) as exc:
        service.reassign_agenda(db, id_agenda=100, target_room_id=2, actor_id=1, confirm_move=False)
    assert exc.value.status_code == 409
    assert exc.value.detail["requires_confirm_move"] is True

    result = service.reassign_agenda(
        db, id_agenda=100, target_room_id=2, actor_id=1, confirm_move=True
    )
    assert result.room_id == 2
    assert db.maps[0].room_id == 2


def test_unassign_requires_confirm():
    db = FakeDB()
    db.maps = [SimpleNamespace(id_agenda=100, room_id=1, updated_at=None, updated_by=None)]

    with pytest.raises(HTTPException) as exc:
        service.reassign_agenda(db, id_agenda=100, target_room_id=None, actor_id=1, confirm_unassign=False)
    assert exc.value.detail["requires_confirm_unassign"] is True

    result = service.reassign_agenda(
        db, id_agenda=100, target_room_id=None, actor_id=1, confirm_unassign=True
    )
    assert result.room_id is None
    assert db.maps == []
