from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class LocationCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    id_dominio: int = Field(gt=0)
    tipo: str = Field(min_length=1, max_length=200)

    @field_validator("tipo")
    @classmethod
    def _strip_tipo(cls, value: str) -> str:
        text = (value or "").strip()
        if not text:
            raise ValueError("tipo es obligatorio")
        return text


class LocationUpdateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    id_dominio: int = Field(gt=0)
    tipo: str = Field(min_length=1, max_length=200)

    @field_validator("tipo")
    @classmethod
    def _strip_tipo(cls, value: str) -> str:
        text = (value or "").strip()
        if not text:
            raise ValueError("tipo es obligatorio")
        return text


class LocationResponse(BaseModel):
    id: int
    name: str
    id_dominio: int
    tipo: str
    created_at: datetime
    updated_at: datetime
