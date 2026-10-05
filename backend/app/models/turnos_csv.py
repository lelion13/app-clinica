from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TurnosCsvImport(Base):
    __tablename__ = "turnos_csv_import"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    row_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)


class TurnosCsvRow(Base):
    __tablename__ = "turnos_csv_row"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    import_id: Mapped[int] = mapped_column(ForeignKey("turnos_csv_import.id", ondelete="CASCADE"), nullable=False, index=True)
    id_persona: Mapped[str | None] = mapped_column(String(64), nullable=True)
    estado: Mapped[str] = mapped_column(String(16), nullable=False)
    nombre: Mapped[str] = mapped_column(String(500), nullable=False)
    nombre_norm: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    id_agenda: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    fecha_reserva: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    fecha_turno: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False, index=True)
    fecha_presente: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    fecha_atencion: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
