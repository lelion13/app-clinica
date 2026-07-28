from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.novedades import NovedadesModulo, NovedadesServicio
from app.schemas.novedades import (
    ModuloCreateRequest,
    ModuloUpdateRequest,
    ServicioCreateRequest,
    ServicioUpdateRequest,
)
from app.services.novedades.helpers import soft_delete


def list_servicios(db: Session, only_active: bool = False) -> list[NovedadesServicio]:
    query = select(NovedadesServicio).where(NovedadesServicio.deleted_at.is_(None)).order_by(NovedadesServicio.id)
    if only_active:
        query = query.where(NovedadesServicio.activo.is_(True))
    return list(db.execute(query).scalars().all())


def create_servicio(db: Session, payload: ServicioCreateRequest, actor_id: int) -> NovedadesServicio:
    name = payload.nombre.strip()
    existing = db.execute(
        select(NovedadesServicio).where(NovedadesServicio.nombre == name, NovedadesServicio.deleted_at.is_(None))
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El servicio ya existe")
    now = datetime.utcnow()
    item = NovedadesServicio(
        nombre=name,
        activo=payload.activo,
        created_at=now,
        updated_at=now,
        created_by=actor_id,
        updated_by=actor_id,
        deleted_at=None,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_servicio(db: Session, servicio_id: int, payload: ServicioUpdateRequest, actor_id: int) -> NovedadesServicio:
    item = db.execute(
        select(NovedadesServicio).where(NovedadesServicio.id == servicio_id, NovedadesServicio.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado")
    item.nombre = payload.nombre.strip()
    item.activo = payload.activo
    item.updated_at = datetime.utcnow()
    item.updated_by = actor_id
    db.commit()
    db.refresh(item)
    return item


def delete_servicio(db: Session, servicio_id: int, actor_id: int) -> None:
    item = db.execute(
        select(NovedadesServicio).where(NovedadesServicio.id == servicio_id, NovedadesServicio.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado")
    soft_delete(item, actor_id)
    db.commit()


def list_modulos(db: Session) -> list[NovedadesModulo]:
    return list(db.execute(select(NovedadesModulo).where(NovedadesModulo.deleted_at.is_(None)).order_by(NovedadesModulo.id)).scalars().all())


def create_modulo(db: Session, payload: ModuloCreateRequest, actor_id: int) -> NovedadesModulo:
    now = datetime.utcnow()
    item = NovedadesModulo(
        descripcion=payload.descripcion.strip(),
        comentario=(payload.comentario or "").strip() or None,
        valor=Decimal(payload.valor),
        created_at=now,
        updated_at=now,
        created_by=actor_id,
        updated_by=actor_id,
        deleted_at=None,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_modulo(db: Session, modulo_id: int, payload: ModuloUpdateRequest, actor_id: int) -> NovedadesModulo:
    item = db.execute(
        select(NovedadesModulo).where(NovedadesModulo.id == modulo_id, NovedadesModulo.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Modulo no encontrado")
    item.descripcion = payload.descripcion.strip()
    item.comentario = (payload.comentario or "").strip() or None
    item.valor = Decimal(payload.valor)
    item.updated_at = datetime.utcnow()
    item.updated_by = actor_id
    db.commit()
    db.refresh(item)
    return item


def delete_modulo(db: Session, modulo_id: int, actor_id: int) -> None:
    item = db.execute(
        select(NovedadesModulo).where(NovedadesModulo.id == modulo_id, NovedadesModulo.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Modulo no encontrado")
    soft_delete(item, actor_id)
    db.commit()
