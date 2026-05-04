import json

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "app-clinica"
    # Wall-clock for consulting rooms / bookings (must match how hours are entered in the UI).
    business_tz: str = Field(default="America/Argentina/Buenos_Aires", validation_alias="BUSINESS_TIMEZONE")
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
    ext_db_enabled: bool = False
    ext_db_engine: str = "mysql"
    ext_db_host: str = ""
    ext_db_port: int = 3306
    ext_db_name: str = ""
    ext_db_user: str = ""
    ext_db_password: str = ""
    ext_db_charset: str = "utf8mb4"
    ext_db_connect_timeout: int = 10
    # PyMySQL: True desactiva SSL (útil si el servidor MySQL no negocia TLS desde el contenedor).
    ext_db_ssl_disabled: bool = Field(default=False, validation_alias="EXT_DB_SSL_DISABLED")
    prof_sync_query: str = (
        "SELECT upe.numero_documento, MAX(upe.nombres) AS nombres, MAX(upe.email) AS email, "
        "MAX(upe.profesion) AS profesion, MAX(upe.tipo_matricula) AS tipo_matricula, "
        "MAX(upe.numero_matricula) AS numero_matricula, "
        "GROUP_CONCAT(DISTINCT upe.especialidad ORDER BY upe.especialidad SEPARATOR ' | ') AS especialidad, "
        "'A' AS estado_usuario "
        "FROM montegrande_usuarios_profesiones_especialidades upe "
        "WHERE upe.profesion = 'MEDICO' "
        "AND upe.matricula_preferida = 'S' "
        "AND upe.estado_usuario = 'A' "
        "AND upe.usuario_estado_institucion = 'A' "
        "AND upe.numero_documento IS NOT NULL "
        "AND TRIM(upe.numero_documento) <> '' "
        "GROUP BY upe.numero_documento"
    )

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
