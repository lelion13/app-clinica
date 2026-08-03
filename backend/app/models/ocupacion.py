from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class OcupacionHorarioActivo(Base):
    """Snapshot de horarios activos (mandante = API externa). Wipe+reload en sync."""

    __tablename__ = "ocupacion_horario_activo"

    id_dato: Mapped[str] = mapped_column(String(80), primary_key=True)
    horario_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    id_agenda: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    id_dominio: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    area_jerarquica_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    nombre_agenda: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tipo: Mapped[str | None] = mapped_column(String(120), nullable=True)
    especialidad_agenda: Mapped[str | None] = mapped_column(String(200), nullable=True)
    medico: Mapped[str | None] = mapped_column(String(200), nullable=True)

    especialidad: Mapped[str | None] = mapped_column(String(200), nullable=True)
    tipo_agenda: Mapped[str | None] = mapped_column(String(80), nullable=True)
    consultorio: Mapped[str | None] = mapped_column(String(120), nullable=True)
    dia: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)
    dia_de_agenda: Mapped[str | None] = mapped_column(String(40), nullable=True)

    fecha_desde: Mapped[str | None] = mapped_column(String(40), nullable=True)
    hora_desde: Mapped[str | None] = mapped_column(String(40), nullable=True)
    fecha_hasta: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)
    hora_hasta: Mapped[str | None] = mapped_column(String(40), nullable=True)
    periodo_desde: Mapped[str | None] = mapped_column(String(40), nullable=True)
    periodo_hasta: Mapped[str | None] = mapped_column(String(40), nullable=True)

    duracion_turno: Mapped[float | None] = mapped_column(Float, nullable=True)
    cantidad_turnos: Mapped[float | None] = mapped_column(Float, nullable=True)
    cantidad_sobreturno: Mapped[float | None] = mapped_column(Float, nullable=True)
    horas_funcionamiento: Mapped[float | None] = mapped_column(Float, nullable=True)
    capacidad_turnos_15_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    tiempo_consultorio: Mapped[float | None] = mapped_column(Float, nullable=True)

    estado_agenda: Mapped[str | None] = mapped_column(String(20), nullable=True)
    estado_horario: Mapped[str | None] = mapped_column(String(20), nullable=True)
    atiende_feriado: Mapped[str | None] = mapped_column(String(8), nullable=True)
    dias_limite_visualizacion_pantalla: Mapped[int | None] = mapped_column(Integer, nullable=True)
    dias_solicitud_turnos: Mapped[int | None] = mapped_column(Integer, nullable=True)

    medico_responsable: Mapped[str | None] = mapped_column(String(200), nullable=True)
    medico_responsable_equipo: Mapped[str | None] = mapped_column(String(200), nullable=True)
    fecha_ultima_modificacion_agenda: Mapped[str | None] = mapped_column(String(40), nullable=True)
    fecha_creacion_horario: Mapped[str | None] = mapped_column(String(40), nullable=True)

    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
