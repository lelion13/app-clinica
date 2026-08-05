from datetime import datetime, time

from sqlalchemy import DateTime, ForeignKey, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.common import AuditMixin


class ConsultingRoom(AuditMixin, Base):
    __tablename__ = "consulting_rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)


class RoomOperatingHour(AuditMixin, Base):
    __tablename__ = "room_operating_hours"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("consulting_rooms.id"), nullable=False)
    weekday: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)


class ConsultingRoomIdAgenda(Base):
    """Mapeo N:1 — varios id_agenda del sync pueden apuntar al mismo consultorio."""

    __tablename__ = "consulting_room_id_agenda"

    id_agenda: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    room_id: Mapped[int] = mapped_column(ForeignKey("consulting_rooms.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
