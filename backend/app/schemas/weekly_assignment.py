from datetime import datetime, time

from pydantic import BaseModel, Field


class WeeklyAssignmentCreateRequest(BaseModel):
    room_id: int
    professional_id: int
    weekday: int = Field(ge=0, le=6, description="0=domingo … 6=sábado (convención JS)")
    start_time: time
    end_time: time


class WeeklyAssignmentConflictBlock(BaseModel):
    weekday: int
    start_time: time
    end_time: time


class WeeklyAssignmentResponse(BaseModel):
    id: int
    room_id: int
    room_code: str
    location_id: int
    professional_id: int
    professional_full_name: str
    weekday: int
    start_time: time
    end_time: time
    created_at: datetime
    updated_at: datetime
