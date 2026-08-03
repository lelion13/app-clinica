from pydantic import BaseModel, ConfigDict, Field


class HorarioActivoItem(BaseModel):
    """Subset de columnas para la grilla Ocupación (v1)."""

    model_config = ConfigDict(extra="ignore")

    id_dato: str | None = None
    id: int | None = None
    id_agenda: int | None = None
    id_dominio: int | None = None
    tipo: str | None = None
    especialidad_agenda: str | None = None
    medico: str | None = None
    especialidad: str | None = None
    dia: str | None = None
    fecha_desde: str | None = None
    hora_desde: str | None = None
    fecha_hasta: str | None = None
    hora_hasta: str | None = None
    duracion_turno: int | float | None = None
    cantidad_turnos: int | float | None = None
    cantidad_sobreturno: int | float | None = None


class HorariosActivosResponse(BaseModel):
    items: list[HorarioActivoItem] = Field(default_factory=list)
