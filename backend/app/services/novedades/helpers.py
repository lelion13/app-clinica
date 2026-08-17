from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.novedades import (
    MotivoSinProduccion,
    NovedadTipo,
    NovedadesConfig,
    NovedadesJefeServicio,
    NovedadesModulo,
    NovedadesPeriodo,
    NovedadesProfesional,
    NovedadesProfesionalServicio,
    NovedadesServicio,
    PeriodoEstado,
)
from app.models.user import User, UserRole

_MOTIVO_VALUES = {m.value for m in MotivoSinProduccion}


def normalize_motivo_sin_produccion(
    motivo: str | None, observacion: str | None
) -> tuple[str | None, str | None]:
    """If either field is provided, both must be valid. Otherwise both None."""
    motivo_s = (motivo or "").strip() or None
    obs_s = (observacion or "").strip() or None
    if motivo_s is None and obs_s is None:
        return None, None
    if motivo_s is None or obs_s is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="motivo_sin_produccion y observacion_sin_produccion deben enviarse juntos",
        )
    if motivo_s not in _MOTIVO_VALUES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="motivo_sin_produccion inválido (vacaciones|enfermedad)",
        )
    return motivo_s, obs_s[:500]


def novedad_valor_calculado(tipo, horas, valor_hora) -> Decimal:
    """Positive for extras; negative for horas_a_descontar."""
    t = tipo.value if isinstance(tipo, NovedadTipo) else str(tipo)
    sign = Decimal("-1") if t == NovedadTipo.horas_a_descontar.value else Decimal("1")
    return sign * Decimal(horas) * Decimal(valor_hora)


def business_today() -> date:
    return datetime.now(ZoneInfo(settings.business_tz)).date()


def get_open_periodo(db: Session) -> NovedadesPeriodo | None:
    return db.execute(
        select(NovedadesPeriodo).where(
            NovedadesPeriodo.deleted_at.is_(None),
            NovedadesPeriodo.estado == PeriodoEstado.open,
        )
    ).scalar_one_or_none()


def require_periodo_open(db: Session, periodo_id: int) -> NovedadesPeriodo:
    periodo = db.execute(
        select(NovedadesPeriodo).where(NovedadesPeriodo.id == periodo_id, NovedadesPeriodo.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not periodo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Periodo no encontrado")
    if periodo.estado != PeriodoEstado.open:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El periodo esta cerrado")
    return periodo


def validate_fecha_realizacion(periodo: NovedadesPeriodo, fecha: date) -> None:
    if fecha < periodo.fecha_inicio or fecha > periodo.fecha_fin:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La fecha de realizacion debe estar dentro del rango del periodo",
        )
    today = business_today()
    if fecha > today:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La fecha de realizacion no puede ser posterior a hoy",
        )


def get_servicio_or_404(db: Session, servicio_id: int) -> NovedadesServicio:
    item = db.execute(
        select(NovedadesServicio).where(NovedadesServicio.id == servicio_id, NovedadesServicio.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado")
    return item


def get_modulo_or_404(db: Session, modulo_id: int) -> NovedadesModulo:
    item = db.execute(
        select(NovedadesModulo).where(NovedadesModulo.id == modulo_id, NovedadesModulo.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Modulo no encontrado")
    return item


def get_professional_or_404(db: Session, professional_id: int, *, require_active: bool = False) -> NovedadesProfesional:
    item = db.execute(
        select(NovedadesProfesional).where(
            NovedadesProfesional.id == professional_id,
            NovedadesProfesional.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profesional no encontrado")
    if require_active and not item.is_active:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El profesional esta inactivo; no se pueden cargar modulos ni novedades",
        )
    return item


def assert_can_load_servicio(db: Session, user: User, servicio_id: int) -> None:
    if user.role == UserRole.admin:
        return
    if user.role != UserRole.jefe_medico:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes")
    link = db.execute(
        select(NovedadesJefeServicio).where(
            NovedadesJefeServicio.user_id == user.id,
            NovedadesJefeServicio.servicio_id == servicio_id,
            NovedadesJefeServicio.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Servicio fuera de alcance")


def assert_can_manage_profesional_servicio(db: Session, user: User, servicio_id: int) -> None:
    """Admin/rrhh: todos los servicios. Jefe: solo los asociados."""
    if user.role in (UserRole.admin, UserRole.rrhh):
        return
    assert_can_load_servicio(db, user, servicio_id)


def require_profesional_en_servicio(db: Session, professional_id: int, servicio_id: int) -> None:
    link = db.execute(
        select(NovedadesProfesionalServicio).where(
            NovedadesProfesionalServicio.professional_id == professional_id,
            NovedadesProfesionalServicio.servicio_id == servicio_id,
            NovedadesProfesionalServicio.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if not link:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El profesional no esta asociado al servicio (ABM Parametrizacion)",
        )


def list_servicios_for_user(db: Session, user: User) -> list[NovedadesServicio]:
    query = select(NovedadesServicio).where(NovedadesServicio.deleted_at.is_(None)).order_by(NovedadesServicio.id)
    if user.role == UserRole.jefe_medico:
        query = (
            select(NovedadesServicio)
            .join(NovedadesJefeServicio, NovedadesJefeServicio.servicio_id == NovedadesServicio.id)
            .where(
                NovedadesServicio.deleted_at.is_(None),
                NovedadesJefeServicio.deleted_at.is_(None),
                NovedadesJefeServicio.user_id == user.id,
            )
            .order_by(NovedadesServicio.id)
        )
    return list(db.execute(query).scalars().all())


def scoped_servicio_ids(db: Session, user: User) -> list[int] | None:
    """None = sin filtro (admin/rrhh). Lista (posible vacía) = alcance de jefe_medico."""
    if user.role != UserRole.jefe_medico:
        return None
    return [item.id for item in list_servicios_for_user(db, user)]


def get_or_create_config(db: Session) -> NovedadesConfig:
    item = db.execute(select(NovedadesConfig).where(NovedadesConfig.id == 1)).scalar_one_or_none()
    if item:
        return item
    now = datetime.utcnow()
    item = NovedadesConfig(
        id=1,
        valor_hora=0,
        created_at=now,
        updated_at=now,
        created_by=None,
        updated_by=None,
        deleted_at=None,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def soft_delete(item, actor_id: int) -> None:
    item.deleted_at = datetime.utcnow()
    item.updated_at = datetime.utcnow()
    item.updated_by = actor_id
