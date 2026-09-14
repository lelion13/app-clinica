from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

DEFAULT_S3_PREFIX = "clinica-backups/"


class BackupConfigUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    enabled: bool = False
    schedule_type: str = Field(default="daily", description="daily or weekly")
    schedule_time: str = Field(default="03:00", description="HH:MM in 24h format")
    schedule_day_of_week: int | None = Field(default=None, description="0=Monday .. 6=Sunday")
    s3_endpoint_url: str | None = Field(default=None)
    s3_bucket_name: str = Field(default="")
    s3_region_name: str = Field(default="auto")
    s3_access_key_id: str = Field(default="")
    s3_secret_access_key: str | None = Field(
        default=None, description="Leave empty/null to keep existing"
    )
    s3_prefix: str = Field(default=DEFAULT_S3_PREFIX)
    retention_count: int = Field(default=15, ge=1, le=365)


class BackupConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    enabled: bool
    schedule_type: str
    schedule_time: str
    schedule_day_of_week: int | None
    s3_endpoint_url: str | None
    s3_bucket_name: str
    s3_region_name: str
    s3_access_key_id: str
    has_secret_access_key: bool
    s3_prefix: str
    retention_count: int
    updated_at: datetime | None


class BackupLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    trigger_type: str
    status: str
    file_name: str
    file_size_bytes: int | None
    storage_key: str | None
    duration_seconds: float | None
    error_message: str | None
    started_at: datetime
    completed_at: datetime | None


class BackupRunResponse(BaseModel):
    success: bool
    message: str
    log: BackupLogResponse | None = None


class BackupStatusResponse(BaseModel):
    is_running: bool
    last_log: BackupLogResponse | None = None
    next_run_at: datetime | None = None
