from datetime import time
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.schemas.consulting_room import RoomHourReplaceItem
from app.services import consulting_room_service as service


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
        self.rooms = [SimpleNamespace(id=1, code="401", deleted_at=None)]
        self.hours = [
            SimpleNamespace(
                id=10,
                room_id=1,
                weekday=1,
                start_time=time(8, 0),
                end_time=time(12, 0),
                deleted_at=None,
                updated_at=None,
                updated_by=None,
            )
        ]
        self.added = []

    def execute(self, statement):
        ent = str(statement)
        low = ent.lower()
        if "room_operating_hour" in low or "RoomOperatingHour" in ent:
            active = [h for h in self.hours if h.deleted_at is None]
            return FakeResult(active)
        if "ConsultingRoom" in ent or "consulting_rooms" in low:
            return FakeResult(self.rooms)
        return FakeResult([])

    def add(self, item):
        self.added.append(item)
        if not hasattr(item, "id"):
            item.id = 100 + len(self.added)
        if not hasattr(item, "deleted_at"):
            item.deleted_at = None
        self.hours.append(item)

    def commit(self):
        return None

    def rollback(self):
        return None


def test_replace_room_hours_full_replace():
    db = FakeDB()
    result = service.replace_room_hours(
        db,
        1,
        [RoomHourReplaceItem(weekday=2, start_time=time(9, 0), end_time=time(13, 0))],
        actor_id=1,
    )
    assert len(result) == 1
    assert result[0].weekday == 2
    assert result[0].start_time == time(9, 0)
    # old soft-deleted
    assert db.hours[0].deleted_at is not None


def test_replace_room_hours_invalid_range():
    db = FakeDB()
    with pytest.raises(HTTPException) as exc:
        service.replace_room_hours(
            db,
            1,
            [RoomHourReplaceItem(weekday=1, start_time=time(12, 0), end_time=time(8, 0))],
            actor_id=1,
        )
    assert exc.value.status_code == 422
    assert db.hours[0].deleted_at is None


def test_replace_room_hours_room_not_found():
    db = FakeDB()
    db.rooms = []
    with pytest.raises(HTTPException) as exc:
        service.replace_room_hours(
            db,
            99,
            [RoomHourReplaceItem(weekday=1, start_time=time(8, 0), end_time=time(12, 0))],
            actor_id=1,
        )
    assert exc.value.status_code == 404
