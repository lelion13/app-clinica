from datetime import date

from pydantic import BaseModel, Field


class WeekdayHoursPoint(BaseModel):
    weekday_index: int = Field(description="0=Lunes … 6=Domingo (orden ISO)")
    label: str
    booked_hours: float


class RoomHoursRank(BaseModel):
    room_id: int
    room_code: str
    booked_hours: float


class ProfessionalHoursRank(BaseModel):
    professional_id: int
    full_name: str
    booked_hours: float


class StatsSummaryResponse(BaseModel):
    period_start: date
    period_end: date
    enabled_hours: float = Field(description="Suma de horas habilitadas según franjas del consultorio")
    booked_hours: float = Field(description="Horas asignadas semanales proyectadas al período (numerador del % ocupación)")
    occupancy_rate_percent: float = Field(description="booked_hours/enabled_hours*100 si enabled>0, si no 0")
    bookings_count: int = Field(description="Cantidad de ocurrencias de asignaciones en el período")
    booked_hours_filtered: float | None = Field(
        default=None,
        description="Si hay filtro de profesional(es): horas de esas asignaciones (no altera el % ocupación)",
    )
    bookings_count_filtered: int | None = Field(
        default=None,
        description="Si hay filtro de profesional(es): ocurrencias de asignaciones de esos profesionales en el período",
    )
    pie_occupied_hours: float = Field(description="min(booked_hours, enabled_hours) para que torta sume horas habilitadas")
    pie_free_hours: float = Field(description="enabled - pie_occupied (capacidad no usada en la torta)")
    hours_by_weekday: list[WeekdayHoursPoint]
    top_rooms: list[RoomHoursRank]
    top_professionals: list[ProfessionalHoursRank]
