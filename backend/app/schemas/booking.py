from datetime import date, datetime, time

from pydantic import BaseModel, Field, model_validator


class BookingCreateRequest(BaseModel):
    room_id: int
    professional_id: int
    start_at: datetime
    end_at: datetime


class BookingUpdateRequest(BaseModel):
    room_id: int | None = None
    professional_id: int | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None


class BookingResponse(BaseModel):
    id: int
    room_id: int
    professional_id: int
    start_at: datetime
    end_at: datetime
    created_at: datetime
    updated_at: datetime


class BookingRecurringCreateRequest(BaseModel):
    """Genera una reserva por cada ocurrencia del mismo día de la semana entre dos fechas (inclusive)."""

    room_id: int
    professional_id: int
    weekday: int = Field(ge=0, le=6, description="0=domingo … 6=sábado (igual que horarios de consultorio)")
    start_time: time
    end_time: time
    period_start: date
    period_end: date

    @model_validator(mode="after")
    def end_after_start(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time debe ser mayor que start_time")
        if self.period_end < self.period_start:
            raise ValueError("period_end no puede ser anterior a period_start")
        return self
