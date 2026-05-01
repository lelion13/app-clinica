import json
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
    # Use a raw string to avoid pydantic-settings JSON parsing issues for env vars.
    # Accepted formats:
    # - CSV: "https://a.com,https://b.com"
    # - JSON: ["https://a.com","https://b.com"]
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        raw = (self.cors_origins or "").strip()
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


settings = Settings()
