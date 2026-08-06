from pydantic import BaseModel, ConfigDict, Field


class HorarioActivoItem(BaseModel):
    """Fila de grilla / indicadores Ocupación."""

    model_config = ConfigDict(extra="ignore", from_attributes=True)

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


class HorariosActivosSyncResponse(BaseModel):
    synced: int
    skipped: int = 0


class AgendaOcupacionEventExtended(BaseModel):
    row_id: int
    id_dato: str | None = None
    id_agenda: int | None = None
    id_dominio: int | None = None
    location_name: str | None = None
    room_id: int | None = None
    room_code: str | None = None
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


class AgendaOcupacionEvent(BaseModel):
    id: str
    title: str = ""
    start: str
    end: str
    resource_id: str = "unassigned"
    extended: AgendaOcupacionEventExtended


class AgendaResourceColumn(BaseModel):
    id: str
    title: str
    room_id: int | None = None


class AgendaOcupacionEventsResponse(BaseModel):
    events: list[AgendaOcupacionEvent] = Field(default_factory=list)
    resources: list[AgendaResourceColumn] = Field(default_factory=list)


class AgendaFilterOption(BaseModel):
    value: str
    label: str


class AgendaFilterOptionsResponse(BaseModel):
    id_dominio: list[AgendaFilterOption] = Field(default_factory=list)
    tipo: list[AgendaFilterOption] = Field(default_factory=list)
    especialidad: list[AgendaFilterOption] = Field(default_factory=list)
    medico: list[AgendaFilterOption] = Field(default_factory=list)
    dia: list[AgendaFilterOption] = Field(default_factory=list)


class IndicadoresRoomRef(BaseModel):
    id: int
    code: str


class IndicadoresOcupacionResponse(BaseModel):
    date: str
    occupied_hours: float
    enabled_hours: float
    free_hours: float
    occupancy_percent: float | None = None
    rooms_included: int = 0
    rooms_in_pie: int = 0
    rooms_without_hours: list[IndicadoresRoomRef] = Field(default_factory=list)
    rooms_without_agenda: int = 0
