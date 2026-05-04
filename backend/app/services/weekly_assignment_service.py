from datetime import datetime, time

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.consulting_room import ConsultingRoom, RoomOperatingHour
from app.models.professional import Professional
from app.models.weekly_assignment import RoomWeeklyAssignment
from app.schemas.weekly_assignment import WeeklyAssignmentCreateRequest


def _is_30m_step(t: time) -> bool:
    return t.second == 0 and t.microsecond == 0 and t.minute in (0, 30)


def _as_conflict_blocks(item: RoomWeeklyAssignment) -> list[dict]:
    return [
        {
            "weekday": item.weekday,
            "start_time": item.start_time.isoformat(),
            "end_time": item.end_time.isoformat(),
            "room_id": item.room_id,
            "professional_id": item.professional_id,
        }
    ]


def _validate_time_rules(payload: WeeklyAssignmentCreateRequest) -> None:
    if payload.start_time >= payload.end_time:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Rango horario invalido")
    if not _is_30m_step(payload.start_time) or not _is_30m_step(payload.end_time):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Los horarios deben ser en bloques de 30 minutos exactos",
        )


def _ensure_room_and_professional(db: Session, room_id: int, professional_id: int) -> tuple[ConsultingRoom, Professional]:
    room = db.execute(
        select(ConsultingRoom).where(ConsultingRoom.id == room_id, ConsultingRoom.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultorio no encontrado")

    professional = db.execute(
        select(Professional).where(
            Professional.id == professional_id,
            Professional.deleted_at.is_(None),
            Professional.is_active.is_(True),
        )
    ).scalar_one_or_none()
    if not professional:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profesional no encontrado")

    return room, professional


def _ensure_within_operating_hours(db: Session, payload: WeeklyAssignmentCreateRequest) -> None:
    rows = db.execute(
        select(RoomOperatingHour).where(
            RoomOperatingHour.room_id == payload.room_id,
            RoomOperatingHour.weekday == payload.weekday,
            RoomOperatingHour.deleted_at.is_(None),
        )
    ).scalars().all()
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El consultorio está cerrado/no habilitado en ese día",
        )
    if not any(h.start_time <= payload.start_time and h.end_time >= payload.end_time for h in rows):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La asignación queda fuera del horario laboral del consultorio",
        )


def _find_room_overlap(
    db: Session, room_id: int, weekday: int, start_time: time, end_time: time
) -> RoomWeeklyAssignment | None:
    return db.execute(
        select(RoomWeeklyAssignment).where(
            RoomWeeklyAssignment.deleted_at.is_(None),
            RoomWeeklyAssignment.room_id == room_id,
            RoomWeeklyAssignment.weekday == weekday,
            RoomWeeklyAssignment.start_time < end_time,
            RoomWeeklyAssignment.end_time > start_time,
        )
    ).scalar_one_or_none()


def _find_professional_overlap(
    db: Session, professional_id: int, weekday: int, start_time: time, end_time: time
) -> RoomWeeklyAssignment | None:
    return db.execute(
        select(RoomWeeklyAssignment).where(
            RoomWeeklyAssignment.deleted_at.is_(None),
            RoomWeeklyAssignment.professional_id == professional_id,
            RoomWeeklyAssignment.weekday == weekday,
            RoomWeeklyAssignment.start_time < end_time,
            RoomWeeklyAssignment.end_time > start_time,
        )
    ).scalar_one_or_none()


def list_weekly_assignments(
    db: Session,
    location_id: int | None,
    room_id: int | None,
    professional_id: int | None,
    weekday: int | None,
) -> list[RoomWeeklyAssignment]:
    query = (
        select(RoomWeeklyAssignment)
        .join(ConsultingRoom, ConsultingRoom.id == RoomWeeklyAssignment.room_id)
        .where(RoomWeeklyAssignment.deleted_at.is_(None), ConsultingRoom.deleted_at.is_(None))
    )
    if location_id is not None:
        query = query.where(ConsultingRoom.location_id == location_id)
    if room_id is not None:
        query = query.where(RoomWeeklyAssignment.room_id == room_id)
    if professional_id is not None:
        query = query.where(RoomWeeklyAssignment.professional_id == professional_id)
    if weekday is not None:
        query = query.where(RoomWeeklyAssignment.weekday == weekday)

    query = query.order_by(RoomWeeklyAssignment.weekday, RoomWeeklyAssignment.start_time, RoomWeeklyAssignment.room_id)
    return list(db.execute(query).scalars().all())


def create_weekly_assignment(db: Session, payload: WeeklyAssignmentCreateRequest, actor_id: int) -> RoomWeeklyAssignment:
    _validate_time_rules(payload)
    _ensure_room_and_professional(db, payload.room_id, payload.professional_id)
    _ensure_within_operating_hours(db, payload)

    room_overlap = _find_room_overlap(db, payload.room_id, payload.weekday, payload.start_time, payload.end_time)
    if room_overlap:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "ROOM_OVERLAP",
                "message": "Solape de consultorio: ya existe una asignación en ese bloque",
                "conflicts": _as_conflict_blocks(room_overlap),
            },
        )

    prof_overlap = _find_professional_overlap(
        db, payload.professional_id, payload.weekday, payload.start_time, payload.end_time
    )
    if prof_overlap:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "PROFESSIONAL_OVERLAP",
                "message": "Solape de profesional: no puede estar en dos consultorios al mismo horario",
                "conflicts": _as_conflict_blocks(prof_overlap),
            },
        )

    now = datetime.utcnow()
    item = RoomWeeklyAssignment(
        room_id=payload.room_id,
        professional_id=payload.professional_id,
        weekday=payload.weekday,
        start_time=payload.start_time,
        end_time=payload.end_time,
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


def delete_weekly_assignment(db: Session, assignment_id: int, actor_id: int) -> None:
    item = db.execute(
        select(RoomWeeklyAssignment).where(
            RoomWeeklyAssignment.id == assignment_id,
            RoomWeeklyAssignment.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asignación semanal no encontrada")
    item.deleted_at = datetime.utcnow()
    item.updated_at = datetime.utcnow()
    item.updated_by = actor_id
    db.commit()
