from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class MeResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool
