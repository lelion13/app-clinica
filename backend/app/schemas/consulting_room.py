from datetime import datetime, time

from pydantic import BaseModel, Field


class ConsultingRoomCreateRequest(BaseModel):
    location_id: int
    code: str = Field(min_length=1, max_length=50)


class ConsultingRoomUpdateRequest(BaseModel):
    location_id: int | None = None
    code: str | None = Field(default=None, min_length=1, max_length=50)


class ConsultingRoomResponse(BaseModel):
    id: int
    location_id: int
    code: str
    created_at: datetime
    updated_at: datetime


class RoomOperatingHourCreateRequest(BaseModel):
    room_id: int
    weekday: int = Field(ge=0, le=6, description="0=domingo … 6=sabado (como JavaScript Date.getDay)")
    start_time: time
    end_time: time


class RoomOperatingHourUpdateRequest(BaseModel):
    weekday: int | None = Field(default=None, ge=0, le=6)
    start_time: time | None = None
    end_time: time | None = None


class RoomOperatingHourResponse(BaseModel):
    id: int
    room_id: int
    weekday: int
    start_time: time
    end_time: time
    created_at: datetime
    updated_at: datetime
