from datetime import datetime

from pydantic import BaseModel, Field


class LocationCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)


class LocationUpdateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)


class LocationResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime
