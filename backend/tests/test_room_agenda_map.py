"""Tests room agenda map — per weekday."""

from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.schemas.consulting_room import RoomIdAgendaReplaceItem
from app.services import room_agenda_map as service


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


def _ocup(id_agenda, dia, h_desde="09:00", h_hasta="11:00", nombre="DOC"):
    return SimpleNamespace(
        id=1,
        id_dato="x",
        tipo=None,
        especialidad_agenda=None,
        medico=nombre,
        fecha_hasta="2026-12-31",
        payload={
            "id_agenda": id_agenda,
            "nombre_agenda": f"TIPO - ESP - {nombre}",
            "medico": nombre,
            "dia": dia,
            "hora_desde": h_desde,
            "hora_hasta": h_hasta,
            "fecha_desde": "2026-01-01",
            "fecha_hasta": "2026-12-31",
        },
    )


class FakeDB:
    def __init__(self):
        self.rooms = [
            SimpleNamespace(id=1, code="401", deleted_at=None),
            SimpleNamespace(id=2, code="402", deleted_at=None),
        ]
        self.maps = []
        self.ocupacion = [
            _ocup(100, "lunes", nombre="APECECHEA"),
            _ocup(100, "martes", nombre="APECECHEA"),
            _ocup(200, "lunes", nombre="PEREZ"),
        ]
        self.deleted = []
        self.added = []

    def execute(self, statement):
        ent = str(statement)
        low = ent.lower()
        if "consulting_room_id_agenda" in low or "ConsultingRoomIdAgenda" in ent:
            return FakeResult(list(self.maps))
        if "ocupacion" in low or "OcupacionHorarioActivo" in ent:
            return FakeResult(self.ocupacion)
        return FakeResult(self.rooms)

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


def test_lookup_by_medico():
    db = FakeDB()
    result = service.lookup_agendas_by_medico(db, "apece")
    assert len(result.items) == 1
    assert result.items[0].id_agenda == 100
    assert result.items[0].current_room_id is None


def test_lookup_includes_current_room_when_full():
    db = FakeDB()
    # lunes=1, martes=2 JS
    db.maps = [
        SimpleNamespace(id_agenda=100, weekday=1, room_id=1),
        SimpleNamespace(id_agenda=100, weekday=2, room_id=1),
    ]
    result = service.lookup_agendas_by_medico(db, "apece")
    assert result.items[0].current_room_id == 1
    assert result.items[0].current_room_code == "401"


def test_list_partial_vs_full(monkeypatch):
    db = FakeDB()
    monkeypatch.setattr(service, "_ensure_room", lambda _db, rid: next(r for r in db.rooms if r.id == rid))

    db.maps = [SimpleNamespace(id_agenda=100, weekday=1, room_id=1)]
    partial = service.list_room_id_agendas(db, 1)
    assert len(partial.items) == 1
    assert partial.items[0].weekday == 1
    assert "lunes" in partial.items[0].label

    db.maps = [
        SimpleNamespace(id_agenda=100, weekday=1, room_id=1),
        SimpleNamespace(id_agenda=100, weekday=2, room_id=1),
    ]
    full = service.list_room_id_agendas(db, 1)
    assert len(full.items) == 1
    assert full.items[0].weekday is None
    assert "lunes" not in full.items[0].label


def test_add_only_pending_days(monkeypatch):
    db = FakeDB()
    monkeypatch.setattr(service, "_ensure_room", lambda _db, rid: next(r for r in db.rooms if r.id == rid))
    monkeypatch.setattr(
        service.reassign_svc,
        "validate_assign_weekday",
        lambda *_a, **_k: None,
    )

    # lunes already on room 2 → only martes pending
    db.maps = [SimpleNamespace(id_agenda=100, weekday=1, room_id=2)]
    item = service.add_room_id_agenda(db, 1, 100, actor_id=1)
    assert item.id_agenda == 100
    assert any(m.weekday == 2 and m.room_id == 1 for m in db.maps)
    assert any(m.weekday == 1 and m.room_id == 2 for m in db.maps)


def test_add_no_pending(monkeypatch):
    db = FakeDB()
    monkeypatch.setattr(service, "_ensure_room", lambda _db, rid: next(r for r in db.rooms if r.id == rid))
    db.maps = [
        SimpleNamespace(id_agenda=100, weekday=1, room_id=1),
        SimpleNamespace(id_agenda=100, weekday=2, room_id=1),
    ]
    with pytest.raises(HTTPException) as exc:
        service.add_room_id_agenda(db, 1, 100, actor_id=1)
    assert exc.value.detail["code"] == "no_pending_days"


def test_replace_assign_pending_all_or_nothing(monkeypatch):
    db = FakeDB()
    monkeypatch.setattr(service, "_ensure_room", lambda _db, rid: next(r for r in db.rooms if r.id == rid))

    calls = []

    def validate(_db, id_agenda, room_id, weekday):
        calls.append(weekday)
        if weekday == 2:
            raise HTTPException(
                status_code=422,
                detail={"message": "solape martes", "conflicts": [{"type": "overlap", "message": "solape martes"}]},
            )

    monkeypatch.setattr(service.reassign_svc, "validate_assign_weekday", validate)

    with pytest.raises(HTTPException) as exc:
        service.replace_room_id_agendas(
            db,
            1,
            [RoomIdAgendaReplaceItem(id_agenda=100, confirm_move=False)],
            actor_id=1,
        )
    assert exc.value.detail["code"] == "validation_failed"
    assert db.maps == []  # nada persistido


def test_replace_keep_and_remove_day(monkeypatch):
    db = FakeDB()
    monkeypatch.setattr(service, "_ensure_room", lambda _db, rid: next(r for r in db.rooms if r.id == rid))
    monkeypatch.setattr(service.reassign_svc, "validate_assign_weekday", lambda *_a, **_k: None)

    db.maps = [
        SimpleNamespace(id_agenda=100, weekday=1, room_id=1),
        SimpleNamespace(id_agenda=100, weekday=2, room_id=1),
    ]
    # Keep only lunes (partial row)
    result = service.replace_room_id_agendas(
        db,
        1,
        [RoomIdAgendaReplaceItem(id_agenda=100, weekday=1, weekdays=[1])],
        actor_id=1,
    )
    assert len(db.maps) == 1
    assert db.maps[0].weekday == 1
    assert result.items[0].weekday == 1
