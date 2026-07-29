from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.novedades import (
    NovedadesAsignacionModulo,
    NovedadesJefeServicio,
    NovedadesNovedad,
    NovedadesProfesionalServicio,
    NovedadesServicio,
)
from app.models.professional import Professional
from app.models.user import User, UserRole
from app.schemas.novedades import (
    AsignacionCreateRequest,
    AsignacionUpdateRequest,
    JefeServicioCreateRequest,
    NovedadCreateRequest,
    NovedadUpdateRequest,
    PeriodoCreateRequest,
    ProfesionalServicioCreateRequest,
)
from app.services.novedades.helpers import (
    assert_can_load_servicio,
    assert_can_manage_profesional_servicio,
    get_modulo_or_404,
    get_professional_or_404,
    get_servicio_or_404,
    require_periodo_open,
    require_profesional_en_servicio,
    scoped_servicio_ids,
    soft_delete,
    validate_fecha_realizacion,
)
from app.models.novedades import NovedadesPeriodo, PeriodoEstado
from app.services.novedades.helpers import get_open_periodo


def list_periodos(db: Session) -> list[NovedadesPeriodo]:
    return list(
        db.execute(select(NovedadesPeriodo).where(NovedadesPeriodo.deleted_at.is_(None)).order_by(NovedadesPeriodo.id.desc()))
        .scalars()
        .all()
    )


def create_periodo(db: Session, payload: PeriodoCreateRequest, actor_id: int) -> NovedadesPeriodo:
    if payload.fecha_fin < payload.fecha_inicio:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Rango de fechas invalido")
    if payload.open_now and get_open_periodo(db):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un periodo abierto")
    now = datetime.utcnow()
    item = NovedadesPeriodo(
        nombre=(payload.nombre or "").strip() or None,
        fecha_inicio=payload.fecha_inicio,
        fecha_fin=payload.fecha_fin,
        estado=PeriodoEstado.open if payload.open_now else PeriodoEstado.closed,
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


def close_periodo(db: Session, periodo_id: int, actor_id: int) -> NovedadesPeriodo:
    item = db.execute(
        select(NovedadesPeriodo).where(NovedadesPeriodo.id == periodo_id, NovedadesPeriodo.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Periodo no encontrado")
    if item.estado == PeriodoEstado.closed:
        return item
    item.estado = PeriodoEstado.closed
    item.updated_at = datetime.utcnow()
    item.updated_by = actor_id
    db.commit()
    db.refresh(item)
    return item


def reopen_periodo(db: Session, periodo_id: int, actor_id: int) -> NovedadesPeriodo:
    item = db.execute(
        select(NovedadesPeriodo).where(NovedadesPeriodo.id == periodo_id, NovedadesPeriodo.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Periodo no encontrado")
    open_one = get_open_periodo(db)
    if open_one and open_one.id != item.id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un periodo abierto")
    item.estado = PeriodoEstado.open
    item.updated_at = datetime.utcnow()
    item.updated_by = actor_id
    db.commit()
    db.refresh(item)
    return item


def list_jefe_servicios(db: Session) -> list[tuple]:
    links = list(
        db.execute(select(NovedadesJefeServicio).where(NovedadesJefeServicio.deleted_at.is_(None)).order_by(NovedadesJefeServicio.id))
        .scalars()
        .all()
    )
    result = []
    for link in links:
        user = db.execute(select(User).where(User.id == link.user_id)).scalar_one_or_none()
        servicio = db.execute(select(NovedadesServicio).where(NovedadesServicio.id == link.servicio_id)).scalar_one_or_none()
        result.append((link, user, servicio))
    return result


def create_jefe_servicio(db: Session, payload: JefeServicioCreateRequest, actor_id: int) -> NovedadesJefeServicio:
    get_servicio_or_404(db, payload.servicio_id)
    user = db.execute(select(User).where(User.id == payload.user_id, User.deleted_at.is_(None))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    if user.role != UserRole.jefe_medico:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El usuario debe tener rol jefe_medico")
    existing = db.execute(
        select(NovedadesJefeServicio).where(
            NovedadesJefeServicio.user_id == payload.user_id,
            NovedadesJefeServicio.servicio_id == payload.servicio_id,
            NovedadesJefeServicio.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La asociacion ya existe")
    now = datetime.utcnow()
    item = NovedadesJefeServicio(
        user_id=payload.user_id,
        servicio_id=payload.servicio_id,
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


def delete_jefe_servicio(db: Session, link_id: int, actor_id: int) -> None:
    item = db.execute(
        select(NovedadesJefeServicio).where(NovedadesJefeServicio.id == link_id, NovedadesJefeServicio.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asociacion no encontrada")
    soft_delete(item, actor_id)
    db.commit()


def list_profesional_servicios(db: Session, user: User) -> list[tuple]:
    links = list(
        db.execute(
            select(NovedadesProfesionalServicio)
            .where(NovedadesProfesionalServicio.deleted_at.is_(None))
            .order_by(NovedadesProfesionalServicio.id)
        )
        .scalars()
        .all()
    )
    alcance = scoped_servicio_ids(db, user)
    if alcance is not None:
        if not alcance:
            return []
        links = [link for link in links if link.servicio_id in alcance]
    result = []
    for link in links:
        professional = db.execute(select(Professional).where(Professional.id == link.professional_id)).scalar_one_or_none()
        servicio = db.execute(select(NovedadesServicio).where(NovedadesServicio.id == link.servicio_id)).scalar_one_or_none()
        result.append((link, professional, servicio))
    return result


def create_profesional_servicio(
    db: Session, payload: ProfesionalServicioCreateRequest, user: User
) -> NovedadesProfesionalServicio:
    get_servicio_or_404(db, payload.servicio_id)
    get_professional_or_404(db, payload.professional_id)
    assert_can_manage_profesional_servicio(db, user, payload.servicio_id)
    existing = db.execute(
        select(NovedadesProfesionalServicio).where(
            NovedadesProfesionalServicio.professional_id == payload.professional_id,
            NovedadesProfesionalServicio.servicio_id == payload.servicio_id,
            NovedadesProfesionalServicio.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La asociacion ya existe")
    now = datetime.utcnow()
    item = NovedadesProfesionalServicio(
        professional_id=payload.professional_id,
        servicio_id=payload.servicio_id,
        created_at=now,
        updated_at=now,
        created_by=user.id,
        updated_by=user.id,
        deleted_at=None,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def delete_profesional_servicio(db: Session, link_id: int, user: User) -> None:
    item = db.execute(
        select(NovedadesProfesionalServicio).where(
            NovedadesProfesionalServicio.id == link_id,
            NovedadesProfesionalServicio.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asociacion no encontrada")
    assert_can_manage_profesional_servicio(db, user, item.servicio_id)
    soft_delete(item, user.id)
    db.commit()


def list_asignaciones(db: Session, user: User) -> list[NovedadesAsignacionModulo]:
    query = (
        select(NovedadesAsignacionModulo)
        .join(NovedadesServicio, NovedadesServicio.id == NovedadesAsignacionModulo.servicio_id)
        .join(Professional, Professional.id == NovedadesAsignacionModulo.professional_id)
        .where(NovedadesAsignacionModulo.deleted_at.is_(None))
    )
    alcance = scoped_servicio_ids(db, user)
    if alcance is not None:
        if not alcance:
            return []
        query = query.where(NovedadesAsignacionModulo.servicio_id.in_(alcance))
    query = query.order_by(
        NovedadesServicio.nombre.asc(),
        Professional.full_name.asc(),
        NovedadesAsignacionModulo.id.desc(),
    )
    return list(db.execute(query).scalars().all())


def create_asignacion(db: Session, payload: AsignacionCreateRequest, user: User) -> NovedadesAsignacionModulo:
    periodo = require_periodo_open(db, payload.periodo_id)
    validate_fecha_realizacion(periodo, payload.fecha_realizacion)
    get_servicio_or_404(db, payload.servicio_id)
    get_professional_or_404(db, payload.professional_id)
    get_modulo_or_404(db, payload.modulo_id)
    assert_can_load_servicio(db, user, payload.servicio_id)
    require_profesional_en_servicio(db, payload.professional_id, payload.servicio_id)
    from app.services.novedades.masters import require_modulo_en_servicio

    require_modulo_en_servicio(db, payload.modulo_id, payload.servicio_id)
    now = datetime.utcnow()
    item = NovedadesAsignacionModulo(
        periodo_id=payload.periodo_id,
        servicio_id=payload.servicio_id,
        professional_id=payload.professional_id,
        modulo_id=payload.modulo_id,
        fecha_realizacion=payload.fecha_realizacion,
        created_at=now,
        updated_at=now,
        created_by=user.id,
        updated_by=user.id,
        deleted_at=None,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_asignacion(db: Session, item_id: int, payload: AsignacionUpdateRequest, user: User) -> NovedadesAsignacionModulo:
    item = db.execute(
        select(NovedadesAsignacionModulo).where(
            NovedadesAsignacionModulo.id == item_id,
            NovedadesAsignacionModulo.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asignacion no encontrada")
    periodo = require_periodo_open(db, item.periodo_id)
    assert_can_load_servicio(db, user, item.servicio_id)
    if payload.modulo_id is None and payload.fecha_realizacion is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Nada para actualizar")
    if payload.modulo_id is not None:
        get_modulo_or_404(db, payload.modulo_id)
        from app.services.novedades.masters import require_modulo_en_servicio

        require_modulo_en_servicio(db, payload.modulo_id, item.servicio_id)
        item.modulo_id = payload.modulo_id
    if payload.fecha_realizacion is not None:
        validate_fecha_realizacion(periodo, payload.fecha_realizacion)
        item.fecha_realizacion = payload.fecha_realizacion
    item.updated_at = datetime.utcnow()
    item.updated_by = user.id
    db.commit()
    db.refresh(item)
    return item


def delete_asignacion(db: Session, item_id: int, user: User) -> None:
    item = db.execute(
        select(NovedadesAsignacionModulo).where(
            NovedadesAsignacionModulo.id == item_id,
            NovedadesAsignacionModulo.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asignacion no encontrada")
    require_periodo_open(db, item.periodo_id)
    assert_can_load_servicio(db, user, item.servicio_id)
    soft_delete(item, user.id)
    db.commit()


def list_novedades(db: Session, user: User) -> list[NovedadesNovedad]:
    query = (
        select(NovedadesNovedad)
        .join(NovedadesServicio, NovedadesServicio.id == NovedadesNovedad.servicio_id)
        .join(Professional, Professional.id == NovedadesNovedad.professional_id)
        .where(NovedadesNovedad.deleted_at.is_(None))
    )
    alcance = scoped_servicio_ids(db, user)
    if alcance is not None:
        if not alcance:
            return []
        query = query.where(NovedadesNovedad.servicio_id.in_(alcance))
    query = query.order_by(
        NovedadesServicio.nombre.asc(),
        Professional.full_name.asc(),
        NovedadesNovedad.id.desc(),
    )
    return list(db.execute(query).scalars().all())


def create_novedad(db: Session, payload: NovedadCreateRequest, user: User) -> NovedadesNovedad:
    from app.models.novedades import NovedadTipo

    periodo = require_periodo_open(db, payload.periodo_id)
    validate_fecha_realizacion(periodo, payload.fecha_realizacion)
    get_servicio_or_404(db, payload.servicio_id)
    get_professional_or_404(db, payload.professional_id)
    assert_can_load_servicio(db, user, payload.servicio_id)
    require_profesional_en_servicio(db, payload.professional_id, payload.servicio_id)
    now = datetime.utcnow()
    item = NovedadesNovedad(
        periodo_id=payload.periodo_id,
        servicio_id=payload.servicio_id,
        professional_id=payload.professional_id,
        tipo=NovedadTipo(payload.tipo),
        horas=payload.horas,
        fecha_realizacion=payload.fecha_realizacion,
        created_at=now,
        updated_at=now,
        created_by=user.id,
        updated_by=user.id,
        deleted_at=None,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_novedad(db: Session, item_id: int, payload: NovedadUpdateRequest, user: User) -> NovedadesNovedad:
    from app.models.novedades import NovedadTipo

    item = db.execute(
        select(NovedadesNovedad).where(NovedadesNovedad.id == item_id, NovedadesNovedad.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novedad no encontrada")
    periodo = require_periodo_open(db, item.periodo_id)
    assert_can_load_servicio(db, user, item.servicio_id)
    if payload.tipo is None and payload.horas is None and payload.fecha_realizacion is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Nada para actualizar")
    if payload.tipo is not None:
        item.tipo = NovedadTipo(payload.tipo)
    if payload.horas is not None:
        item.horas = payload.horas
    if payload.fecha_realizacion is not None:
        validate_fecha_realizacion(periodo, payload.fecha_realizacion)
        item.fecha_realizacion = payload.fecha_realizacion
    item.updated_at = datetime.utcnow()
    item.updated_by = user.id
    db.commit()
    db.refresh(item)
    return item


def delete_novedad(db: Session, item_id: int, user: User) -> None:
    item = db.execute(
        select(NovedadesNovedad).where(NovedadesNovedad.id == item_id, NovedadesNovedad.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novedad no encontrada")
    require_periodo_open(db, item.periodo_id)
    assert_can_load_servicio(db, user, item.servicio_id)
    soft_delete(item, user.id)
    db.commit()
