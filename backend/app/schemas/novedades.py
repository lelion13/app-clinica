from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator


def _normalize_concepto_liquidacion(value: int | None) -> int | None:
    if value is None or value == 0:
        return None
    if value < 0:
        raise ValueError("concepto_liquidacion debe ser un entero positivo o vacío")
    return value


class ServicioCreateRequest(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    activo: bool = True
    valor_hora: Decimal = Field(default=Decimal("0"), ge=0)
    concepto_liquidacion: int | None = None

    @field_validator("concepto_liquidacion")
    @classmethod
    def _concepto_create(cls, value: int | None) -> int | None:
        return _normalize_concepto_liquidacion(value)


class ServicioUpdateRequest(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    activo: bool = True
    valor_hora: Decimal = Field(ge=0)
    concepto_liquidacion: int | None = None

    @field_validator("concepto_liquidacion")
    @classmethod
    def _concepto_update(cls, value: int | None) -> int | None:
        return _normalize_concepto_liquidacion(value)


class ServicioResponse(BaseModel):
    id: int
    nombre: str
    activo: bool
    valor_hora: Decimal
    concepto_liquidacion: int | None = None
    created_at: datetime
    updated_at: datetime


class ModuloCreateRequest(BaseModel):
    descripcion: str = Field(min_length=2, max_length=200)
    comentario: str | None = Field(default=None, max_length=500)
    valor: Decimal = Field(ge=0)
    produccion: bool = False
    sadofe: bool = False
    servicio_ids: list[int] = Field(min_length=1)


class ModuloUpdateRequest(BaseModel):
    descripcion: str = Field(min_length=2, max_length=200)
    comentario: str | None = Field(default=None, max_length=500)
    valor: Decimal = Field(ge=0)
    produccion: bool = False
    sadofe: bool = False


class ModuloServiciosUpdateRequest(BaseModel):
    servicio_ids: list[int] = Field(default_factory=list)


class ModuloResponse(BaseModel):
    id: int
    descripcion: str
    comentario: str | None
    valor: Decimal
    produccion: bool = False
    sadofe: bool = False
    servicio_ids: list[int] = []
    servicio_nombres: list[str] = []
    created_at: datetime
    updated_at: datetime


class PeriodoCreateRequest(BaseModel):
    nombre: str | None = Field(default=None, max_length=120)
    fecha_inicio: date
    fecha_fin: date
    open_now: bool = True


class PeriodoResponse(BaseModel):
    id: int
    nombre: str | None
    fecha_inicio: date
    fecha_fin: date
    estado: str
    created_at: datetime
    updated_at: datetime


class FeriadoCreateRequest(BaseModel):
    fecha: date
    nombre: str = Field(min_length=2, max_length=200)


class FeriadoUpdateRequest(BaseModel):
    fecha: date
    nombre: str = Field(min_length=2, max_length=200)


class FeriadoResponse(BaseModel):
    id: int
    fecha: date
    nombre: str
    created_at: datetime
    updated_at: datetime


class JefeServicioCreateRequest(BaseModel):
    user_id: int
    servicio_id: int


class JefeServicioResponse(BaseModel):
    id: int
    user_id: int
    user_name: str | None = None
    user_email: str | None = None
    servicio_id: int
    servicio_nombre: str | None = None
    created_at: datetime


class ProfesionalServicioCreateRequest(BaseModel):
    professional_id: int
    servicio_id: int


class ProfesionalServicioResponse(BaseModel):
    id: int
    professional_id: int
    professional_name: str | None = None
    professional_codprof: str | None = None
    professional_is_active: bool | None = None
    servicio_id: int
    servicio_nombre: str | None = None
    created_at: datetime


class ProfesionalDirectoryItem(BaseModel):
    id: int
    full_name: str
    codprof: str | None = None
    legajo: str | None = None
    license_number: str | None = None
    external_document: str | None = None
    specialty: str | None = None
    is_active: bool


class NovedadesProfSyncResponse(BaseModel):
    created: int
    updated: int
    inactivated: int
    skipped: int
    errors: list[str]
    synced_at: datetime


class NovedadesTransaccionalPurgeResponse(BaseModel):
    deleted_asignaciones: int
    deleted_novedades: int
    deleted_profesional_servicios: int


MotivoSinProduccionLiteral = Literal["vacaciones", "enfermedad"]


class AsignacionCreateRequest(BaseModel):
    periodo_id: int
    servicio_id: int
    professional_id: int
    modulo_id: int
    fecha_realizacion: date
    motivo_sin_produccion: MotivoSinProduccionLiteral | None = None
    observacion_sin_produccion: str | None = Field(default=None, max_length=500)


class AsignacionUpdateRequest(BaseModel):
    modulo_id: int | None = None
    fecha_realizacion: date | None = None


class AsignacionResponse(BaseModel):
    id: int
    periodo_id: int
    periodo_nombre: str | None = None
    servicio_id: int
    servicio_nombre: str | None = None
    professional_id: int
    professional_name: str | None = None
    professional_codprof: str | None = None
    modulo_id: int
    modulo_descripcion: str | None = None
    modulo_valor: Decimal | None = None
    fecha_realizacion: date
    motivo_sin_produccion: str | None = None
    observacion_sin_produccion: str | None = None
    created_at: datetime
    updated_at: datetime
    created_by: int | None = None


NovedadTipoLiteral = Literal["hora_extra", "hora_extra_por_ausencia", "horas_a_descontar"]


class NovedadCreateRequest(BaseModel):
    periodo_id: int
    servicio_id: int
    professional_id: int
    tipo: NovedadTipoLiteral
    horas: int = Field(ge=1)
    fecha_realizacion: date
    motivo_sin_produccion: MotivoSinProduccionLiteral | None = None
    observacion_sin_produccion: str | None = Field(default=None, max_length=500)


class NovedadUpdateRequest(BaseModel):
    tipo: NovedadTipoLiteral | None = None
    horas: int | None = Field(default=None, ge=1)
    fecha_realizacion: date | None = None


class NovedadResponse(BaseModel):
    id: int
    periodo_id: int
    periodo_nombre: str | None = None
    servicio_id: int
    servicio_nombre: str | None = None
    professional_id: int
    professional_name: str | None = None
    professional_codprof: str | None = None
    tipo: str
    tipo_label: str
    horas: Decimal
    valor_calculado: Decimal | None = None
    fecha_realizacion: date
    motivo_sin_produccion: str | None = None
    observacion_sin_produccion: str | None = None
    created_at: datetime
    updated_at: datetime
    created_by: int | None = None


class TieneProduccionResponse(BaseModel):
    tiene_produccion: bool


class GridRowResponse(BaseModel):
    tipo: str
    id: int
    periodo_id: int
    periodo_nombre: str | None
    servicio_id: int
    servicio_nombre: str
    professional_id: int
    professional_name: str
    concepto: str
    horas: Decimal | None = None
    valor: Decimal | None
    valor_hora: Decimal | None = None
    cargado_por: str | None
    fecha_realizacion: date | None = None
    fecha_carga: datetime


class BonoColumnaResponse(BaseModel):
    key: str
    label: str
    centro: str
    servicio: str
    semana: str
    horario: str
    kind: Literal["cantidad", "subtotal"] = "cantidad"
    opcion_key: str | None = None


class CapitalHumanoRowResponse(BaseModel):
    professional_id: int
    legajo: str | None = None
    professional_name: str
    monto_cargas: Decimal
    monto_ajustes: Decimal
    monto_bonos: int = 0
    monto_total: Decimal
    bonos: dict[str, int] = Field(default_factory=dict)
    bonos_subtotales: dict[str, int] = Field(default_factory=dict)


class CapitalHumanoGridResponse(BaseModel):
    columns: list[BonoColumnaResponse] = Field(default_factory=list)
    rows: list[CapitalHumanoRowResponse] = Field(default_factory=list)
    opciones_sin_tarifa: list[str] = Field(default_factory=list)


class BonoOpcionResponse(BaseModel):
    id: int
    key: str
    label: str
    centro: str
    servicio: str
    semana: str
    horario: str


class ProduccionTarifaCreateRequest(BaseModel):
    opcion_id: int
    valor_unitario: int = Field(ge=0)


class ProduccionTarifaBulkCreateRequest(BaseModel):
    opcion_ids: list[int] = Field(min_length=1)
    valor_unitario: int = Field(ge=0)


class ProduccionTarifaUpdateRequest(BaseModel):
    valor_unitario: int = Field(ge=0)


class ProduccionTarifaResponse(BaseModel):
    id: int
    opcion_id: int
    key: str
    label: str
    centro: str
    servicio: str
    semana: str
    horario: str
    valor_unitario: int
    created_at: datetime
    updated_at: datetime


class BonosImportRequest(BaseModel):
    periodo_id: int


class BonosImportResponse(BaseModel):
    received: int
    matched: int
    solo_bonos: int
    columns: int
    ignored: int


class SoloBonoRowResponse(BaseModel):
    professional_id: int
    codprof: str
    legajo: str | None = None
    professional_name: str
    bonos: dict[str, int] = Field(default_factory=dict)
    total_cantidad: int


class AjusteCapitalCreateRequest(BaseModel):
    professional_id: int
    periodo_id: int
    servicio_id: int | None = None
    importe: Decimal
    comentario: str = Field(min_length=1, max_length=500)


class AjusteCapitalResponse(BaseModel):
    id: int
    professional_id: int
    periodo_id: int
    servicio_id: int | None
    importe: Decimal
    comentario: str
    created_at: datetime
    created_by: int | None = None
    created_by_name: str | None = None
