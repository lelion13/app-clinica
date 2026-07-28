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
    servicio_id: int
    servicio_nombre: str | None = None
    created_at: datetime


class ProfesionalDirectoryItem(BaseModel):
    id: int
    full_name: str
    license_number: str | None = None
    specialty: str | None = None
    is_active: bool


class AsignacionCreateRequest(BaseModel):
    periodo_id: int
    servicio_id: int
    professional_id: int
    modulo_id: int


class AsignacionUpdateRequest(BaseModel):
    modulo_id: int


class AsignacionResponse(BaseModel):
    id: int
    periodo_id: int
    servicio_id: int
    professional_id: int
    modulo_id: int
    modulo_descripcion: str | None = None
    modulo_valor: Decimal | None = None
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


class NovedadUpdateRequest(BaseModel):
    tipo: NovedadTipoLiteral
    horas: int = Field(ge=1)


class NovedadResponse(BaseModel):
    id: int
    periodo_id: int
    servicio_id: int
    professional_id: int
    tipo: str
    tipo_label: str
    horas: Decimal
    valor_calculado: Decimal | None = None
    created_at: datetime
    updated_at: datetime
    created_by: int | None = None


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
    fecha_carga: datetime
