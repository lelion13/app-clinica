import json
from typing import Annotated

from pydantic import BeforeValidator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _empty_str_to_none(value):
    if value is None:
        return None
    if isinstance(value, str) and not value.strip():
        return None
    return value


def _optional_bool(value):
    value = _empty_str_to_none(value)
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "t", "yes", "y", "on"}:
            return True
        if lowered in {"0", "false", "f", "no", "n", "off"}:
            return False
    return value


def _optional_int(value, default: int):
    value = _empty_str_to_none(value)
    if value is None:
        return default
    return value


OptionalBool = Annotated[bool, BeforeValidator(_optional_bool)]
SmtpPort = Annotated[int, BeforeValidator(lambda v: _optional_int(v, 587))]


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
    # Sync HTTP de profesionales para Novedades (no Distribución).
    novedades_prof_sync_url: str = Field(default="", validation_alias="NOVEDADES_PROF_SYNC_URL")
    novedades_prof_sync_token: str = Field(default="", validation_alias="NOVEDADES_PROF_SYNC_TOKEN")
    novedades_prof_sync_timeout: float = Field(default=30.0, validation_alias="NOVEDADES_PROF_SYNC_TIMEOUT")
    novedades_bonos_resumen_url: str = Field(
        default="https://api.cpmgsa.com.ar:8001/bonos/resumen",
        validation_alias="NOVEDADES_BONOS_RESUMEN_URL",
    )
    novedades_bonos_resumen_timeout: float = Field(
        default=60.0, validation_alias="NOVEDADES_BONOS_RESUMEN_TIMEOUT"
    )
    novedades_bonos_practicas_url: str = Field(
        default="",
        validation_alias="NOVEDADES_BONOS_PRACTICAS_URL",
    )
    novedades_bonos_practicas_timeout: float = Field(
        default=60.0, validation_alias="NOVEDADES_BONOS_PRACTICAS_TIMEOUT"
    )
    novedades_bonos_internaciones_url: str = Field(
        default="",
        validation_alias="NOVEDADES_BONOS_INTERNACIONES_URL",
    )
    novedades_bonos_internaciones_timeout: float = Field(
        default=60.0, validation_alias="NOVEDADES_BONOS_INTERNACIONES_TIMEOUT"
    )
    novedades_bonos_tiene_produccion_url: str = Field(
        default="https://api.cpmgsa.com.ar:8001/bonos/tiene-produccion",
        validation_alias="NOVEDADES_BONOS_TIENE_PRODUCCION_URL",
    )
    novedades_bonos_tiene_produccion_timeout: float = Field(
        default=30.0, validation_alias="NOVEDADES_BONOS_TIENE_PRODUCCION_TIMEOUT"
    )
    novedades_prof_especialistas_url: str = Field(
        default="",
        validation_alias="NOVEDADES_PROF_ESPECIALISTAS_URL",
    )
    novedades_prof_especialistas_timeout: float = Field(
        default=30.0,
        validation_alias="NOVEDADES_PROF_ESPECIALISTAS_TIMEOUT",
    )
    # Proxy HTTP horarios activos (Distribución → Ocupación). Token: NOVEDADES_PROF_SYNC_TOKEN.
    distribucion_horarios_activos_url: str = Field(
        default="",
        validation_alias="DISTRIBUCION_HORARIOS_ACTIVOS_URL",
    )
    distribucion_horarios_activos_timeout: float = Field(
        default=120.0,
        validation_alias="DISTRIBUCION_HORARIOS_ACTIVOS_TIMEOUT",
    )
    # Public web origin for password-reset links (no trailing slash).
    app_public_url: str = Field(default="http://localhost:5173", validation_alias="APP_PUBLIC_URL")
    smtp_host: str = Field(default="", validation_alias="SMTP_HOST")
    smtp_port: SmtpPort = Field(default=587, validation_alias="SMTP_PORT")
    smtp_user: str = Field(default="", validation_alias="SMTP_USER")
    smtp_pass: str = Field(default="", validation_alias="SMTP_PASS")
    smtp_from: str = Field(default="", validation_alias="SMTP_FROM")
    # false = STARTTLS (typical 587); true = implicit TLS/SSL (typical 465).
    # Empty env value is treated as false (avoids crash on SMTP_SECURE=).
    smtp_secure: OptionalBool = Field(default=False, validation_alias="SMTP_SECURE")
    password_reset_ttl_minutes: int = Field(default=60, validation_alias="PASSWORD_RESET_TTL_MINUTES")
    password_reset_cooldown_seconds: int = Field(
        default=60, validation_alias="PASSWORD_RESET_COOLDOWN_SECONDS"
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
