from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.services import room_agenda_map as service


class FakeScalars:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items

    def first(self):
        return self._items[0] if self._items else None


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
            SimpleNamespace(id=1, code="401", deleted_at=None),
            SimpleNamespace(id=2, code="402", deleted_at=None),
        ]
        self.maps = []
        self.ocupacion = [
            SimpleNamespace(
                payload={
                    "id_agenda": 100,
                    "nombre_agenda": "ART - TRAUMA - APECECHEA",
                    "medico": "APECECHEA",
                },
                medico="APECECHEA",
            ),
            SimpleNamespace(
                payload={
                    "id_agenda": 200,
                    "nombre_agenda": "SC - CLINICA - PEREZ",
                    "medico": "PEREZ",
                },
                medico="PEREZ",
            ),
        ]
        self.deleted = []
        self.added = []

    def execute(self, statement):
        sql = str(statement).lower()
        if "consulting_room_id_agenda" in sql or "ConsultingRoomIdAgenda" in str(statement):
            # distinguish by filters roughly via current maps content for tests
            return FakeResult(list(self.maps))
        if "ocupacion" in sql or "OcupacionHorarioActivo" in str(statement):
            return FakeResult(self.ocupacion)
        # rooms
        return FakeResult(self.rooms)

    def add(self, item):
        self.added.append(item)
        self.maps.append(item)

    def delete(self, item):
        self.deleted.append(item)
        self.maps = [m for m in self.maps if m is not item]

    def commit(self):
        return None


def test_lookup_by_medico():
    db = FakeDB()
    result = service.lookup_agendas_by_medico(db, "apece")
    assert len(result.items) == 1
    assert result.items[0].id_agenda == 100
    assert "100 —" in result.items[0].label


def test_add_and_conflict_requires_confirm(monkeypatch):
    db = FakeDB()

    def ensure(_db, room_id):
        return next(r for r in db.rooms if r.id == room_id)

    monkeypatch.setattr(service, "_ensure_room", ensure)
    monkeypatch.setattr(service, "_label_for_id_agenda", lambda _db, i: str(i))

    # Patch execute for targeted map lookups
    original_execute = db.execute

    def execute(statement):
        ent = str(statement)
        if "ConsultingRoomIdAgenda" in ent or "consulting_room_id_agenda" in ent.lower():
            # SQLAlchemy select with where id_agenda == X — return matching
            return FakeResult(list(db.maps))
        if "ConsultingRoom" in ent or "consulting_rooms" in ent.lower():
            return FakeResult(db.rooms)
        return original_execute(statement)

    db.execute = execute

    item = service.add_room_id_agenda(db, 1, 100, actor_id=1, confirm_move=False)
    assert item.id_agenda == 100
    assert len(db.maps) == 1
    assert db.maps[0].room_id == 1

    with pytest.raises(HTTPException) as exc:
        service.add_room_id_agenda(db, 2, 100, actor_id=1, confirm_move=False)
    assert exc.value.status_code == 409
    assert exc.value.detail["requires_confirm_move"] is True

    moved = service.add_room_id_agenda(db, 2, 100, actor_id=1, confirm_move=True)
    assert moved.id_agenda == 100
    assert db.maps[0].room_id == 2
