from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.models.novedades import PeriodoEstado
from app.models.user import UserRole
from app.schemas.novedades import (
    AsignacionCreateRequest,
    NovedadCreateRequest,
    PeriodoCreateRequest,
    PeriodoUpdateRequest,
)
from app.services.novedades import cargas as cargas_service
from app.services.novedades.helpers import (
    assert_can_load_servicio,
    normalize_motivo_sin_produccion,
    require_periodo_open,
)
from app.services.novedades.prof_sync import modulo_valor_para_profesional


class FakeResult:
    def __init__(self, value):
        self._value = value

    def scalar_one_or_none(self):
        return self._value

    def scalars(self):
        return self

    def first(self):
        return self.scalar_one_or_none()

    def all(self):
        return self._value if isinstance(self._value, list) else []


class FakeDB:
    def __init__(self):
        self.added = []
        self.committed = False

    def execute(self, _stmt):
        return FakeResult(None)

    def add(self, item):
        self.added.append(item)

    def commit(self):
        self.committed = True

    def refresh(self, item):
        if getattr(item, "id", None) is None:
            item.id = 1


def test_require_periodo_open_blocks_closed():
    closed = SimpleNamespace(id=1, estado=PeriodoEstado.closed, deleted_at=None)

    class DB:
        def execute(self, _stmt):
            return FakeResult(closed)

    with pytest.raises(HTTPException) as exc:
        require_periodo_open(DB(), 1)
    assert exc.value.status_code == 409


def test_assert_can_load_servicio_blocks_unscoped_jefe():
    user = SimpleNamespace(id=9, role=UserRole.jefe_medico)

    class DB:
        def execute(self, _stmt):
            return FakeResult(None)

    with pytest.raises(HTTPException) as exc:
        assert_can_load_servicio(DB(), user, servicio_id=3)
    assert exc.value.status_code == 403


def test_scoped_servicio_ids_none_for_admin():
    from app.services.novedades.helpers import scoped_servicio_ids

    user = SimpleNamespace(id=1, role=UserRole.admin)
    assert scoped_servicio_ids(FakeDB(), user) is None


def test_scoped_servicio_ids_returns_list_for_jefe(monkeypatch):
    from app.services.novedades import helpers as helpers_mod

    user = SimpleNamespace(id=9, role=UserRole.jefe_medico)
    monkeypatch.setattr(
        helpers_mod,
        "list_servicios_for_user",
        lambda _db, _user: [SimpleNamespace(id=2), SimpleNamespace(id=5)],
    )
    assert helpers_mod.scoped_servicio_ids(FakeDB(), user) == [2, 5]


def test_create_periodo_rejects_second_open(monkeypatch):
    db = FakeDB()
    monkeypatch.setattr(cargas_service, "get_open_periodo", lambda _db: SimpleNamespace(id=99))
    payload = PeriodoCreateRequest(
        nombre="P2",
        fecha_inicio=date(2026, 7, 1),
        fecha_fin=date(2026, 7, 31),
        open_now=True,
    )
    with pytest.raises(HTTPException) as exc:
        cargas_service.create_periodo(db, payload, actor_id=1)
    assert exc.value.status_code == 409


def test_novedad_create_request_requires_horas_positive():
    with pytest.raises(Exception):
        NovedadCreateRequest(
            periodo_id=1,
            servicio_id=1,
            professional_id=1,
            tipo="hora_extra",
            horas=0,
            fecha_realizacion=date(2026, 7, 15),
        )


def test_novedad_tipos_validos():
    payload = NovedadCreateRequest(
        periodo_id=1,
        servicio_id=1,
        professional_id=1,
        tipo="hora_extra_por_ausencia",
        horas=3,
        fecha_realizacion=date(2026, 7, 15),
    )
    assert payload.tipo == "hora_extra_por_ausencia"
    assert payload.horas == 3
    assert payload.fecha_realizacion == date(2026, 7, 15)


def test_novedad_horas_rechaza_decimal():
    with pytest.raises(Exception):
        NovedadCreateRequest(
            periodo_id=1,
            servicio_id=1,
            professional_id=1,
            tipo="hora_extra",
            horas=1.5,
            fecha_realizacion=date(2026, 7, 15),
        )


def test_validate_fecha_realizacion_fuera_periodo(monkeypatch):
    from app.services.novedades.helpers import validate_fecha_realizacion

    periodo = SimpleNamespace(fecha_inicio=date(2026, 7, 1), fecha_fin=date(2026, 7, 31))
    monkeypatch.setattr("app.services.novedades.helpers.business_today", lambda: date(2026, 7, 20))
    with pytest.raises(HTTPException) as exc:
        validate_fecha_realizacion(periodo, date(2026, 6, 15))
    assert exc.value.status_code == 422


def test_validate_fecha_realizacion_futura(monkeypatch):
    from app.services.novedades.helpers import validate_fecha_realizacion

    periodo = SimpleNamespace(fecha_inicio=date(2026, 7, 1), fecha_fin=date(2026, 7, 31))
    monkeypatch.setattr("app.services.novedades.helpers.business_today", lambda: date(2026, 7, 20))
    with pytest.raises(HTTPException) as exc:
        validate_fecha_realizacion(periodo, date(2026, 7, 21))
    assert exc.value.status_code == 422


def test_validate_fecha_realizacion_ok(monkeypatch):
    from app.services.novedades.helpers import validate_fecha_realizacion

    periodo = SimpleNamespace(fecha_inicio=date(2026, 7, 1), fecha_fin=date(2026, 7, 31))
    monkeypatch.setattr("app.services.novedades.helpers.business_today", lambda: date(2026, 7, 20))
    validate_fecha_realizacion(periodo, date(2026, 7, 15))


def test_export_xlsx_content_type_bytes(monkeypatch):
    from app.services.novedades import export_xls

    monkeypatch.setattr(export_xls, "build_grid_rows", lambda *args, **kwargs: [])
    content = export_xls.export_xlsx_bytes(FakeDB())
    assert isinstance(content, (bytes, bytearray))
    assert content[:2] == b"PK"


def test_normalize_motivo_ambos_none():
    assert normalize_motivo_sin_produccion(None, None) == (None, None)
    assert normalize_motivo_sin_produccion("", "  ") == (None, None)


def test_normalize_motivo_requiere_ambos():
    with pytest.raises(HTTPException) as exc:
        normalize_motivo_sin_produccion("vacaciones", None)
    assert exc.value.status_code == 422
    with pytest.raises(HTTPException) as exc2:
        normalize_motivo_sin_produccion(None, "nota")
    assert exc2.value.status_code == 422


def test_normalize_motivo_enum_y_trim():
    m, o = normalize_motivo_sin_produccion("enfermedad", "  licencia  ")
    assert m == "enfermedad"
    assert o == "licencia"
    with pytest.raises(HTTPException) as exc:
        normalize_motivo_sin_produccion("otro", "x")
    assert exc.value.status_code == 422


def _stub_create_deps(monkeypatch):
    periodo = SimpleNamespace(
        id=1,
        estado=PeriodoEstado.open,
        deleted_at=None,
        fecha_inicio=date(2026, 7, 1),
        fecha_fin=date(2026, 7, 31),
    )
    monkeypatch.setattr(cargas_service, "require_periodo_open", lambda _db, _id: periodo)
    monkeypatch.setattr(cargas_service, "validate_fecha_realizacion", lambda *_a, **_k: None)
    monkeypatch.setattr(cargas_service, "get_servicio_or_404", lambda *_a, **_k: SimpleNamespace(id=1))
    monkeypatch.setattr(
        cargas_service,
        "get_professional_or_404",
        lambda *_a, **_k: SimpleNamespace(id=1, es_especialista=False),
    )
    monkeypatch.setattr(
        cargas_service,
        "get_modulo_or_404",
        lambda *_a, **_k: SimpleNamespace(id=1, valor=Decimal("1000")),
    )
    monkeypatch.setattr(cargas_service, "assert_can_load_servicio", lambda *_a, **_k: None)
    monkeypatch.setattr(cargas_service, "require_profesional_en_servicio", lambda *_a, **_k: None)
    monkeypatch.setattr(
        "app.services.novedades.masters.require_modulo_en_servicio",
        lambda *_a, **_k: None,
    )


def test_create_novedad_sin_motivo(monkeypatch):
    _stub_create_deps(monkeypatch)
    db = FakeDB()
    user = SimpleNamespace(id=7, role=UserRole.admin)
    payload = NovedadCreateRequest(
        periodo_id=1,
        servicio_id=1,
        professional_id=1,
        tipo="hora_extra",
        horas=2,
        fecha_realizacion=date(2026, 7, 15),
    )
    item = cargas_service.create_novedad(db, payload, user)
    assert item.motivo_sin_produccion is None
    assert item.observacion_sin_produccion is None
    assert db.committed


def test_create_novedad_con_motivo(monkeypatch):
    _stub_create_deps(monkeypatch)
    db = FakeDB()
    user = SimpleNamespace(id=7, role=UserRole.admin)
    payload = NovedadCreateRequest(
        periodo_id=1,
        servicio_id=1,
        professional_id=1,
        tipo="hora_extra",
        horas=2,
        fecha_realizacion=date(2026, 7, 15),
        motivo_sin_produccion="vacaciones",
        observacion_sin_produccion="viaje familiar",
    )
    item = cargas_service.create_novedad(db, payload, user)
    assert item.motivo_sin_produccion == "vacaciones"
    assert item.observacion_sin_produccion == "viaje familiar"


def test_create_asignacion_con_motivo(monkeypatch):
    _stub_create_deps(monkeypatch)
    db = FakeDB()
    user = SimpleNamespace(id=7, role=UserRole.admin)
    payload = AsignacionCreateRequest(
        periodo_id=1,
        servicio_id=1,
        professional_id=1,
        modulo_id=3,
        fecha_realizacion=date(2026, 7, 15),
        motivo_sin_produccion="enfermedad",
        observacion_sin_produccion="certificado médico",
    )
    item = cargas_service.create_asignacion(db, payload, user)
    assert item.motivo_sin_produccion == "enfermedad"
    assert item.observacion_sin_produccion == "certificado médico"
    assert item.valor == Decimal("1000")


def test_modulo_valor_especialista_factor():
    assert modulo_valor_para_profesional(Decimal("1000"), es_especialista=False) == Decimal("1000")
    assert modulo_valor_para_profesional(Decimal("1000"), es_especialista=True) == Decimal("1200.00")


def test_create_asignacion_especialista_aplica_plus(monkeypatch):
    _stub_create_deps(monkeypatch)
    monkeypatch.setattr(
        cargas_service,
        "get_professional_or_404",
        lambda *_a, **_k: SimpleNamespace(id=1, es_especialista=True),
    )
    db = FakeDB()
    user = SimpleNamespace(id=7, role=UserRole.admin)
    payload = AsignacionCreateRequest(
        periodo_id=1,
        servicio_id=1,
        professional_id=1,
        modulo_id=3,
        fecha_realizacion=date(2026, 7, 15),
    )
    item = cargas_service.create_asignacion(db, payload, user)
    assert item.valor == Decimal("1200.00")


def test_update_periodo_success():
    periodo = SimpleNamespace(
        id=1,
        nombre="Viejo",
        fecha_inicio=date(2026, 8, 1),
        fecha_fin=date(2026, 8, 31),
        estado=PeriodoEstado.open,
        deleted_at=None,
    )

    class DB:
        def __init__(self):
            self.committed = False
            self.query_count = 0

        def execute(self, _stmt):
            self.query_count += 1
            if self.query_count == 1:
                return FakeResult(periodo)
            # Cargas out of range
            return FakeResult(None)

        def commit(self):
            self.committed = True

        def refresh(self, _item):
            pass

    db = DB()
    payload = PeriodoUpdateRequest(
        nombre="Nuevo Agosto",
        fecha_inicio=date(2026, 8, 5),
        fecha_fin=date(2026, 8, 25),
    )
    res = cargas_service.update_periodo(db, 1, payload, actor_id=10)
    assert res.nombre == "Nuevo Agosto"
    assert res.fecha_inicio == date(2026, 8, 5)
    assert res.fecha_fin == date(2026, 8, 25)
    assert db.committed


def test_update_periodo_blocks_closed():
    periodo = SimpleNamespace(
        id=1,
        nombre="Cerrado",
        fecha_inicio=date(2026, 8, 1),
        fecha_fin=date(2026, 8, 31),
        estado=PeriodoEstado.closed,
        deleted_at=None,
    )

    class DB:
        def execute(self, _stmt):
            return FakeResult(periodo)

    db = DB()
    payload = PeriodoUpdateRequest(
        nombre="Intento",
        fecha_inicio=date(2026, 8, 1),
        fecha_fin=date(2026, 8, 31),
    )
    with pytest.raises(HTTPException) as exc:
        cargas_service.update_periodo(db, 1, payload, actor_id=10)
    assert exc.value.status_code == 409


def test_update_periodo_blocks_when_cargas_out_of_range():
    periodo = SimpleNamespace(
        id=1,
        nombre="Abierto",
        fecha_inicio=date(2026, 8, 1),
        fecha_fin=date(2026, 8, 31),
        estado=PeriodoEstado.open,
        deleted_at=None,
    )

    class DB:
        def __init__(self):
            self.query_count = 0

        def execute(self, _stmt):
            self.query_count += 1
            if self.query_count == 1:
                return FakeResult(periodo)
            # Retorna una carga con fecha 2026-08-30 fuera de rango
            return FakeResult(date(2026, 8, 30))

    db = DB()
    payload = PeriodoUpdateRequest(
        nombre="Agosto corto",
        fecha_inicio=date(2026, 8, 1),
        fecha_fin=date(2026, 8, 20),
    )
    with pytest.raises(HTTPException) as exc:
        cargas_service.update_periodo(db, 1, payload, actor_id=10)
    assert exc.value.status_code == 422
    assert "fuera del nuevo rango" in exc.value.detail


def test_delete_periodo_blocks_when_has_cargas():
    periodo = SimpleNamespace(id=1, deleted_at=None)

    class DB:
        def execute(self, _stmt):
            # Retorna el periodo y luego encuentra un modulo asignado
            return FakeResult(1)

    db = DB()
    with pytest.raises(HTTPException) as exc:
        cargas_service.delete_periodo(db, 1, actor_id=10)
    assert exc.value.status_code == 409


def test_delete_periodo_success():
    periodo = SimpleNamespace(id=1, deleted_at=None)

    class DB:
        def __init__(self):
            self.committed = False
            self.count = 0

        def execute(self, _stmt):
            self.count += 1
            if self.count == 1:
                return FakeResult(periodo)
            # checks for asignaciones, novedades, bonos, practicas, internaciones, ajustes
            return FakeResult(None)

        def commit(self):
            self.committed = True

    db = DB()
    cargas_service.delete_periodo(db, 1, actor_id=10)
    assert db.committed
    assert periodo.deleted_at is not None


