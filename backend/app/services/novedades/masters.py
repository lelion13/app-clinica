from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.novedades import NovedadesFeriado, NovedadesModulo, NovedadesModuloServicio, NovedadesServicio
from app.schemas.novedades import (
    FeriadoCreateRequest,
    FeriadoUpdateRequest,
    ModuloCreateRequest,
    ModuloUpdateRequest,
    ServicioCreateRequest,
    ServicioUpdateRequest,
)
from app.services.novedades.helpers import get_servicio_or_404, soft_delete


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
        valor_hora=Decimal(payload.valor_hora),
        concepto_liquidacion=payload.concepto_liquidacion,
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
    item.valor_hora = Decimal(payload.valor_hora)
    item.concepto_liquidacion = payload.concepto_liquidacion
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


def _validate_servicio_ids(db: Session, servicio_ids: list[int], *, allow_empty: bool = False) -> list[int]:
    unique_ids = list(dict.fromkeys(servicio_ids))
    if not unique_ids:
        if allow_empty:
            return []
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Debe asociar al menos un servicio")
    for sid in unique_ids:
        get_servicio_or_404(db, sid)
    return unique_ids


def _set_modulo_servicios(db: Session, modulo_id: int, servicio_ids: list[int], actor_id: int) -> None:
    now = datetime.utcnow()
    desired = set(servicio_ids)
    existing = list(
        db.execute(
            select(NovedadesModuloServicio).where(
                NovedadesModuloServicio.modulo_id == modulo_id,
                NovedadesModuloServicio.deleted_at.is_(None),
            )
        )
        .scalars()
        .all()
    )
    existing_by_servicio = {link.servicio_id: link for link in existing}
    for sid, link in existing_by_servicio.items():
        if sid not in desired:
            soft_delete(link, actor_id)
    for sid in desired:
        if sid in existing_by_servicio:
            continue
        db.add(
            NovedadesModuloServicio(
                modulo_id=modulo_id,
                servicio_id=sid,
                created_at=now,
                updated_at=now,
                created_by=actor_id,
                updated_by=actor_id,
                deleted_at=None,
            )
        )


def list_modulo_servicio_ids(db: Session, modulo_id: int) -> list[int]:
    return list(
        db.execute(
            select(NovedadesModuloServicio.servicio_id).where(
                NovedadesModuloServicio.modulo_id == modulo_id,
                NovedadesModuloServicio.deleted_at.is_(None),
            )
        )
        .scalars()
        .all()
    )


def list_modulo_servicio_nombres(db: Session, modulo_id: int) -> list[str]:
    rows = list(
        db.execute(
            select(NovedadesServicio.nombre)
            .join(NovedadesModuloServicio, NovedadesModuloServicio.servicio_id == NovedadesServicio.id)
            .where(
                NovedadesModuloServicio.modulo_id == modulo_id,
                NovedadesModuloServicio.deleted_at.is_(None),
                NovedadesServicio.deleted_at.is_(None),
            )
            .order_by(NovedadesServicio.nombre)
        )
        .scalars()
        .all()
    )
    return rows


def list_modulos(db: Session, servicio_id: int | None = None) -> list[NovedadesModulo]:
    if servicio_id is None:
        return list(
            db.execute(select(NovedadesModulo).where(NovedadesModulo.deleted_at.is_(None)).order_by(NovedadesModulo.id))
            .scalars()
            .all()
        )
    return list(
        db.execute(
            select(NovedadesModulo)
            .join(NovedadesModuloServicio, NovedadesModuloServicio.modulo_id == NovedadesModulo.id)
            .where(
                NovedadesModulo.deleted_at.is_(None),
                NovedadesModuloServicio.deleted_at.is_(None),
                NovedadesModuloServicio.servicio_id == servicio_id,
            )
            .order_by(NovedadesModulo.id)
        )
        .scalars()
        .all()
    )


def create_modulo(db: Session, payload: ModuloCreateRequest, actor_id: int) -> NovedadesModulo:
    servicio_ids = _validate_servicio_ids(db, payload.servicio_ids)
    now = datetime.utcnow()
    item = NovedadesModulo(
        descripcion=payload.descripcion.strip(),
        comentario=(payload.comentario or "").strip() or None,
        valor=Decimal(payload.valor),
        produccion=bool(payload.produccion),
        sadofe=bool(payload.sadofe),
        created_at=now,
        updated_at=now,
        created_by=actor_id,
        updated_by=actor_id,
        deleted_at=None,
    )
    db.add(item)
    db.flush()
    _set_modulo_servicios(db, item.id, servicio_ids, actor_id)
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
    item.produccion = bool(payload.produccion)
    item.sadofe = bool(payload.sadofe)
    item.updated_at = datetime.utcnow()
    item.updated_by = actor_id
    db.commit()
    db.refresh(item)
    return item


def update_modulo_servicios(
    db: Session, modulo_id: int, servicio_ids: list[int], actor_id: int
) -> NovedadesModulo:
    item = db.execute(
        select(NovedadesModulo).where(NovedadesModulo.id == modulo_id, NovedadesModulo.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Modulo no encontrado")
    validated = _validate_servicio_ids(db, servicio_ids, allow_empty=True)
    item.updated_at = datetime.utcnow()
    item.updated_by = actor_id
    _set_modulo_servicios(db, item.id, validated, actor_id)
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
    links = list(
        db.execute(
            select(NovedadesModuloServicio).where(
                NovedadesModuloServicio.modulo_id == modulo_id,
                NovedadesModuloServicio.deleted_at.is_(None),
            )
        )
        .scalars()
        .all()
    )
    for link in links:
        soft_delete(link, actor_id)
    db.commit()


def require_modulo_en_servicio(db: Session, modulo_id: int, servicio_id: int) -> None:
    link = db.execute(
        select(NovedadesModuloServicio).where(
            NovedadesModuloServicio.modulo_id == modulo_id,
            NovedadesModuloServicio.servicio_id == servicio_id,
            NovedadesModuloServicio.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if not link:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El modulo no esta asociado al servicio",
        )


def list_feriados(db: Session) -> list[NovedadesFeriado]:
    return list(
        db.execute(
            select(NovedadesFeriado)
            .where(NovedadesFeriado.deleted_at.is_(None))
            .order_by(NovedadesFeriado.fecha.asc(), NovedadesFeriado.id.asc())
        )
        .scalars()
        .all()
    )


def _feriado_fecha_taken(db: Session, fecha, *, exclude_id: int | None = None) -> bool:
    query = select(NovedadesFeriado).where(
        NovedadesFeriado.fecha == fecha,
        NovedadesFeriado.deleted_at.is_(None),
    )
    if exclude_id is not None:
        query = query.where(NovedadesFeriado.id != exclude_id)
    return db.execute(query).scalar_one_or_none() is not None


def create_feriado(db: Session, payload: FeriadoCreateRequest, actor_id: int) -> NovedadesFeriado:
    nombre = payload.nombre.strip()
    if _feriado_fecha_taken(db, payload.fecha):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un feriado en esa fecha")
    now = datetime.utcnow()
    item = NovedadesFeriado(
        fecha=payload.fecha,
        nombre=nombre,
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


def update_feriado(db: Session, feriado_id: int, payload: FeriadoUpdateRequest, actor_id: int) -> NovedadesFeriado:
    item = db.execute(
        select(NovedadesFeriado).where(NovedadesFeriado.id == feriado_id, NovedadesFeriado.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feriado no encontrado")
    if _feriado_fecha_taken(db, payload.fecha, exclude_id=feriado_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un feriado en esa fecha")
    item.fecha = payload.fecha
    item.nombre = payload.nombre.strip()
    item.updated_at = datetime.utcnow()
    item.updated_by = actor_id
    db.commit()
    db.refresh(item)
    return item


def delete_feriado(db: Session, feriado_id: int, actor_id: int) -> None:
    item = db.execute(
        select(NovedadesFeriado).where(NovedadesFeriado.id == feriado_id, NovedadesFeriado.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feriado no encontrado")
    soft_delete(item, actor_id)
    db.commit()
