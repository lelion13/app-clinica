from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.novedades import (
    NovedadesJefeServicio,
    NovedadesModulo,
    NovedadesPeriodo,
    NovedadesProfesionalServicio,
    NovedadesServicio,
    PeriodoEstado,
)
from app.models.professional import Professional
from app.models.user import User, UserRole


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


def get_professional_or_404(db: Session, professional_id: int) -> Professional:
    item = db.execute(
        select(Professional).where(Professional.id == professional_id, Professional.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profesional no encontrado")
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


def ensure_profesional_servicio_link(db: Session, professional_id: int, servicio_id: int, actor_id: int) -> None:
    existing = db.execute(
        select(NovedadesProfesionalServicio).where(
            NovedadesProfesionalServicio.professional_id == professional_id,
            NovedadesProfesionalServicio.servicio_id == servicio_id,
            NovedadesProfesionalServicio.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if existing:
        return
    now = datetime.utcnow()
    db.add(
        NovedadesProfesionalServicio(
            professional_id=professional_id,
            servicio_id=servicio_id,
            created_at=now,
            updated_at=now,
            created_by=actor_id,
            updated_by=actor_id,
            deleted_at=None,
        )
    )


def soft_delete(item, actor_id: int) -> None:
    item.deleted_at = datetime.utcnow()
    item.updated_at = datetime.utcnow()
    item.updated_by = actor_id
