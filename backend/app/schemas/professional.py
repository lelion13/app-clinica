from datetime import datetime

from pydantic import BaseModel, Field


class ProfessionalSyncResponse(BaseModel):
    created: int
    updated: int
    inactivated: int
    skipped: int
    errors: list[str]
    synced_at: datetime


class ProfessionalResponse(BaseModel):
    id: int
    full_name: str
    license_number: str | None
    external_document: str | None
    email: str | None
    profession: str | None
    license_type: str | None
    specialty: str | None
    external_status: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
