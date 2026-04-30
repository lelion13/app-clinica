from datetime import datetime

from pydantic import BaseModel


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
