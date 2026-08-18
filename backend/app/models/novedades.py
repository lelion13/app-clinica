import enum
from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.common import AuditMixin


class PeriodoEstado(str, enum.Enum):
    open = "open"
    closed = "closed"


class NovedadTipo(str, enum.Enum):
    hora_extra = "hora_extra"
    hora_extra_por_ausencia = "hora_extra_por_ausencia"
    horas_a_descontar = "horas_a_descontar"


NOVEDAD_TIPO_LABELS = {
    NovedadTipo.hora_extra: "Hora extra",
    NovedadTipo.hora_extra_por_ausencia: "Hora extra por ausencia",
    NovedadTipo.horas_a_descontar: "Horas a descontar",
}


class MotivoSinProduccion(str, enum.Enum):
    vacaciones = "vacaciones"
    enfermedad = "enfermedad"


MOTIVO_SIN_PRODUCCION_LABELS = {
    MotivoSinProduccion.vacaciones: "Vacaciones",
    MotivoSinProduccion.enfermedad: "Enfermedad",
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
    produccion: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sadofe: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


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


class NovedadesFeriado(AuditMixin, Base):
    __tablename__ = "novedades_feriado"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)


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


class NovedadesBonoOpcion(AuditMixin, Base):
    """Dimensión de columna de bonos (centro|servicio|semana|horario)."""

    __tablename__ = "novedades_bono_opcion"
    __table_args__ = (
        UniqueConstraint("centro", "servicio", "semana", "horario", name="uq_novedades_bono_opcion"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    centro: Mapped[str] = mapped_column(String(80), nullable=False)
    servicio: Mapped[str] = mapped_column(String(80), nullable=False)
    semana: Mapped[str] = mapped_column(String(80), nullable=False)
    horario: Mapped[str] = mapped_column(String(80), nullable=False)


class NovedadesBonoCantidad(AuditMixin, Base):
    """Cantidad de bonos por profesional, período y opción."""

    __tablename__ = "novedades_bono_cantidad"
    __table_args__ = (
        UniqueConstraint(
            "periodo_id",
            "professional_id",
            "opcion_id",
            name="uq_novedades_bono_cantidad_scope",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    periodo_id: Mapped[int] = mapped_column(ForeignKey("novedades_periodo.id"), nullable=False)
    professional_id: Mapped[int] = mapped_column(ForeignKey("novedades_profesional.id"), nullable=False)
    opcion_id: Mapped[int] = mapped_column(ForeignKey("novedades_bono_opcion.id"), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)


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
    motivo_sin_produccion: Mapped[str | None] = mapped_column(String(40), nullable=True)
    observacion_sin_produccion: Mapped[str | None] = mapped_column(String(500), nullable=True)


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
    motivo_sin_produccion: Mapped[str | None] = mapped_column(String(40), nullable=True)
    observacion_sin_produccion: Mapped[str | None] = mapped_column(String(500), nullable=True)
