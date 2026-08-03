from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class OcupacionHorarioActivo(Base):
    """Snapshot de horarios activos.

    El endpoint puede repetir `id_dato`; por eso la PK es local (`id`) y
    cada fila del JSON se guarda completa en `payload` (una fila API = una fila DB).
    """

    __tablename__ = "ocupacion_horario_activo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    # Derivados de nombre_agenda (solo UI/indicadores).
    tipo: Mapped[str | None] = mapped_column(String(120), nullable=True)
    especialidad_agenda: Mapped[str | None] = mapped_column(String(200), nullable=True)
    medico: Mapped[str | None] = mapped_column(String(200), nullable=True)
    # Desnormalizado del payload para filtrar vigencia.
    fecha_hasta: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)
    id_dato: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
