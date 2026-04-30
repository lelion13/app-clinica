from datetime import datetime

from pydantic import BaseModel, Field


class ProfessionalCreateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    license_number: str | None = Field(default=None, max_length=80)


class ProfessionalUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    license_number: str | None = Field(default=None, max_length=80)


class ProfessionalResponse(BaseModel):
    id: int
    full_name: str
    license_number: str | None
    created_at: datetime
    updated_at: datetime
