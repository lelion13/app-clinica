import json

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "app-clinica"
    database_url: str = "postgresql+psycopg://app_clinica:app_clinica@db:5432/app_clinica"
    jwt_secret: str = "change_me_super_secret"
    jwt_access_minutes: int = 15
    jwt_refresh_days: int = 7
    bcrypt_rounds: int = 12
    cookie_secure: bool = False
    cookie_samesite: str = "lax"
    cors_origins: list[str] = ["http://localhost:5173"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if value is None:
            return ["http://localhost:5173"]
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return ["http://localhost:5173"]
            if raw.startswith("["):
                try:
                    parsed = json.loads(raw)
                except json.JSONDecodeError as exc:
                    raise ValueError("CORS_ORIGINS invalido: JSON mal formado") from exc
                if not isinstance(parsed, list):
                    raise ValueError("CORS_ORIGINS invalido: debe ser una lista JSON")
                return [str(item).strip() for item in parsed if str(item).strip()]
            return [item.strip() for item in raw.split(",") if item.strip()]
        raise ValueError("CORS_ORIGINS invalido")


settings = Settings()
