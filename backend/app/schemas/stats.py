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
    booked_hours: float = Field(description="Suma de horas de reserva (intersección con el período)")
    occupancy_rate_percent: float = Field(description="booked/enabled*100 si enabled>0, si no 0")
    bookings_count: int
    pie_occupied_hours: float
    pie_free_hours: float = Field(description="max(0, enabled - booked)")
    hours_by_weekday: list[WeekdayHoursPoint]
    top_rooms: list[RoomHoursRank]
    top_professionals: list[ProfessionalHoursRank]
