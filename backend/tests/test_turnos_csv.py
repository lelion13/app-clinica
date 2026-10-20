"""Tests for turnos CSV import / stats."""

from datetime import datetime
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.services.distribucion import turnos_csv as service


def test_normalize_nombre():
    assert service.normalize_nombre("  SEDE PB - REUMATOLOGÍA - DRA ") == service.normalize_nombre(
        "sede pb - reumatologia - dra"
    )


def test_parse_csv_datetime():
    dt = service.parse_csv_datetime("2026-9-7, 16:00:00")
    assert dt == datetime(2026, 9, 7, 16, 0, 0)


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
    def __init__(self):
        self.ocupacion = [
            SimpleNamespace(
                id=1,
                id_dato="a",
                tipo=None,
                especialidad_agenda=None,
                medico=None,
                fecha_hasta=None,
                payload={"id_agenda": 10, "nombre_agenda": "SEDE PB - REUMATOLOGIA - DRA DUARTE"},
            )
        ]
        self.imports = []
        self.rows = []
        self.added = []
        self._id = 1

    def execute(self, statement):
        text = str(statement).lower()
        if "ocupacion" in text or "OcupacionHorarioActivo" in str(statement):
            return FakeResult(self.ocupacion)
        if "turnos_csv_row" in text or "TurnosCsvRow" in str(statement):
            return FakeResult(self.rows)
        if "turnos_csv_import" in text or "TurnosCsvImport" in str(statement):
            return FakeResult(self.imports)
        if "consulting_room" in text:
            return FakeResult([])
        return FakeResult([])

    def add(self, obj):
        self.added.append(obj)
        if obj.__class__.__name__ == "TurnosCsvImport":
            obj.id = self._id
            self._id += 1
            self.imports.append(obj)
        elif obj.__class__.__name__ == "TurnosCsvRow":
            self.rows.append(obj)

    def flush(self):
        return None

    def commit(self):
        return None

    def refresh(self, obj):
        return None


def test_import_rejects_unmatched(monkeypatch):
    db = FakeDB()
    monkeypatch.setattr(service, "_sync_nombre_index", lambda _db: {"sede pb - reumatologia - dra duarte": [10]})

    csv_bytes = (
        "ID Persona,Estado Turno,Nombre,Fecha Turno\n"
        '1,AT,"SEDE PB - REUMATOLOGIA - DRA DUARTE","2026-9-7, 16:00:00"\n'
        '2,AU,"OTRA AGENDA INEXISTENTE","2026-9-8, 10:00:00"\n'
    ).encode("utf-8")

    with pytest.raises(HTTPException) as exc:
        service.import_turnos_csv(db, filename="t.csv", content=csv_bytes, actor_id=1)
    assert exc.value.status_code == 422
    assert exc.value.detail["code"] == "unmatched_nombres"
    assert exc.value.detail["unmatched_count"] == 1


def test_import_ok(monkeypatch):
    db = FakeDB()
    monkeypatch.setattr(service, "_sync_nombre_index", lambda _db: {"sede pb - reumatologia - dra duarte": [10]})

    csv_bytes = (
        "ID Persona,Estado Turno,Nombre,Fecha Reserva,Fecha Turno,Fecha Presente,Fecha Atencion\n"
        '1,AT,"SEDE PB - REUMATOLOGIA - DRA DUARTE","2026-6-1, 14:00:00","2026-9-7, 16:00:00","2026-9-7, 15:50:00","2026-9-7, 16:20:00"\n'
        '2,AU,"SEDE PB - REUMATOLOGIA - DRA DUARTE","2026-6-2, 10:00:00","2026-9-8, 10:00:00",,\n'
    ).encode("utf-8")

    result = service.import_turnos_csv(db, filename="092026_cmg.csv", content=csv_bytes, actor_id=1)
    assert result.row_count == 2
    assert result.period_start == "2026-09-07"
    assert result.period_end == "2026-09-08"
    assert len(db.rows) == 2
