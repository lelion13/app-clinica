import enum
from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.common import AuditMixin


class PeriodoEstado(str, enum.Enum):
    open = "open"
    closed = "closed"


class NovedadTipo(str, enum.Enum):
    hora_extra = "hora_extra"
    hora_extra_por_ausencia = "hora_extra_por_ausencia"


NOVEDAD_TIPO_LABELS = {
    NovedadTipo.hora_extra: "Hora extra",
    NovedadTipo.hora_extra_por_ausencia: "Hora extra por ausencia",
}


class NovedadesServicio(AuditMixin, Base):
    __tablename__ = "novedades_servicio"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    valor_hora: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))


class NovedadesModulo(AuditMixin, Base):
    __tablename__ = "novedades_modulo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    descripcion: Mapped[str] = mapped_column(String(200), nullable=False)
    comentario: Mapped[str | None] = mapped_column(String(500), nullable=True)
    valor: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)


class NovedadesModuloServicio(AuditMixin, Base):
    __tablename__ = "novedades_modulo_servicio"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    modulo_id: Mapped[int] = mapped_column(ForeignKey("novedades_modulo.id"), nullable=False)
    servicio_id: Mapped[int] = mapped_column(ForeignKey("novedades_servicio.id"), nullable=False)


class NovedadesPeriodo(AuditMixin, Base):
    __tablename__ = "novedades_periodo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str | None] = mapped_column(String(120), nullable=True)
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[date] = mapped_column(Date, nullable=False)
    estado: Mapped[PeriodoEstado] = mapped_column(
        Enum(PeriodoEstado, name="periodoestado", native_enum=False),
        nullable=False,
        default=PeriodoEstado.open,
    )


class NovedadesConfig(AuditMixin, Base):
    __tablename__ = "novedades_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    valor_hora: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))


class NovedadesJefeServicio(AuditMixin, Base):
    __tablename__ = "novedades_jefe_servicio"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    servicio_id: Mapped[int] = mapped_column(ForeignKey("novedades_servicio.id"), nullable=False)


class NovedadesProfesional(AuditMixin, Base):
    """Catálogo de profesionales solo para Novedades (sync HTTP por CODPROF)."""

    __tablename__ = "novedades_profesional"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codprof: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    codprov: Mapped[str | None] = mapped_column(String(40), nullable=True)
    legajo: Mapped[str | None] = mapped_column(String(40), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class NovedadesAjusteCapital(AuditMixin, Base):
    """Ajuste (+/−) de Capital Humano por profesional y período (± servicio)."""

    __tablename__ = "novedades_ajuste_capital"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    professional_id: Mapped[int] = mapped_column(ForeignKey("novedades_profesional.id"), nullable=False)
    periodo_id: Mapped[int] = mapped_column(ForeignKey("novedades_periodo.id"), nullable=False)
    servicio_id: Mapped[int | None] = mapped_column(ForeignKey("novedades_servicio.id"), nullable=True)
    importe: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    comentario: Mapped[str] = mapped_column(String(500), nullable=False)


class NovedadesProfesionalServicio(AuditMixin, Base):
    __tablename__ = "novedades_profesional_servicio"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    professional_id: Mapped[int] = mapped_column(ForeignKey("novedades_profesional.id"), nullable=False)
    servicio_id: Mapped[int] = mapped_column(ForeignKey("novedades_servicio.id"), nullable=False)


class NovedadesAsignacionModulo(AuditMixin, Base):
    __tablename__ = "novedades_asignacion_modulo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    periodo_id: Mapped[int] = mapped_column(ForeignKey("novedades_periodo.id"), nullable=False)
    servicio_id: Mapped[int] = mapped_column(ForeignKey("novedades_servicio.id"), nullable=False)
    professional_id: Mapped[int] = mapped_column(ForeignKey("novedades_profesional.id"), nullable=False)
    modulo_id: Mapped[int] = mapped_column(ForeignKey("novedades_modulo.id"), nullable=False)
    fecha_realizacion: Mapped[date] = mapped_column(Date, nullable=False)


class NovedadesNovedad(AuditMixin, Base):
    __tablename__ = "novedades_novedad"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    periodo_id: Mapped[int] = mapped_column(ForeignKey("novedades_periodo.id"), nullable=False)
    servicio_id: Mapped[int] = mapped_column(ForeignKey("novedades_servicio.id"), nullable=False)
    professional_id: Mapped[int] = mapped_column(ForeignKey("novedades_profesional.id"), nullable=False)
    tipo: Mapped[NovedadTipo] = mapped_column(
        Enum(NovedadTipo, name="novedadtipo", native_enum=False),
        nullable=False,
    )
    horas: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    fecha_realizacion: Mapped[date] = mapped_column(Date, nullable=False)
