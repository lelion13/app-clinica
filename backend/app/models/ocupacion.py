from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class OcupacionHorarioActivo(Base):
    """Snapshot de horarios activos. `payload` = JSON exacto del endpoint (mandante)."""

    __tablename__ = "ocupacion_horario_activo"

    id_dato: Mapped[str] = mapped_column(String(120), primary_key=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    # Derivados de nombre_agenda (no vienen del endpoint; solo para UI/indicadores).
    tipo: Mapped[str | None] = mapped_column(String(120), nullable=True)
    especialidad_agenda: Mapped[str | None] = mapped_column(String(200), nullable=True)
    medico: Mapped[str | None] = mapped_column(String(200), nullable=True)
    # Desnormalizado del payload para filtrar vigencia sin parsear JSONB.
    fecha_hasta: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
