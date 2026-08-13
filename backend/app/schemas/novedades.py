from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class ServicioCreateRequest(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    activo: bool = True
    valor_hora: Decimal = Field(default=Decimal("0"), ge=0)


class ServicioUpdateRequest(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    activo: bool = True
    valor_hora: Decimal = Field(ge=0)


class ServicioResponse(BaseModel):
    id: int
    nombre: str
    activo: bool
    valor_hora: Decimal
    created_at: datetime
    updated_at: datetime


class ModuloCreateRequest(BaseModel):
    descripcion: str = Field(min_length=2, max_length=200)
    comentario: str | None = Field(default=None, max_length=500)
    valor: Decimal = Field(ge=0)
    servicio_ids: list[int] = Field(min_length=1)


class ModuloUpdateRequest(BaseModel):
    descripcion: str = Field(min_length=2, max_length=200)
    comentario: str | None = Field(default=None, max_length=500)
    valor: Decimal = Field(ge=0)
    servicio_ids: list[int] = Field(min_length=1)


class ModuloResponse(BaseModel):
    id: int
    descripcion: str
    comentario: str | None
    valor: Decimal
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


NovedadTipoLiteral = Literal["hora_extra", "hora_extra_por_ausencia"]


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


class CapitalHumanoRowResponse(BaseModel):
    professional_id: int
    legajo: str | None = None
    professional_name: str
    monto_cargas: Decimal
    monto_ajustes: Decimal
    monto_total: Decimal
    bonos: dict[str, int] = Field(default_factory=dict)


class CapitalHumanoGridResponse(BaseModel):
    columns: list[BonoColumnaResponse] = Field(default_factory=list)
    rows: list[CapitalHumanoRowResponse] = Field(default_factory=list)


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
