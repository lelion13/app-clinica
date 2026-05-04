from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.calendar import weekday_js_from_date, weekday_js_from_local_datetime
from app.core.config import settings
from app.models.booking import Booking
from app.models.consulting_room import ConsultingRoom, RoomOperatingHour
from app.models.professional import Professional
from app.schemas.booking import BookingCreateRequest, BookingRecurringCreateRequest, BookingUpdateRequest


def _to_business_local(dt: datetime) -> datetime:
    """Interpret booking instants in the clinic timezone for hour/weekday checks."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.astimezone(ZoneInfo(settings.business_tz))


def _daterange_inclusive(start: date, end: date):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def _ensure_room_and_professional(db: Session, room_id: int, professional_id: int) -> None:
    room = db.execute(select(ConsultingRoom).where(ConsultingRoom.id == room_id, ConsultingRoom.deleted_at.is_(None))).scalar_one_or_none()
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


def _validate_operating_hours(db: Session, room_id: int, start_at: datetime, end_at: datetime) -> None:
    start_local = _to_business_local(start_at)
    end_local = _to_business_local(end_at)
    if start_local >= end_local:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Rango horario invalido")
    if start_local.date() != end_local.date():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="La reserva debe iniciar y terminar el mismo dia")

    weekday = weekday_js_from_local_datetime(start_local)
    schedule = db.execute(
        select(RoomOperatingHour).where(
            and_(
                RoomOperatingHour.room_id == room_id,
                RoomOperatingHour.weekday == weekday,
                RoomOperatingHour.deleted_at.is_(None),
                RoomOperatingHour.start_time <= start_local.time(),
                RoomOperatingHour.end_time >= end_local.time(),
            )
        )
    ).scalar_one_or_none()
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La reserva queda fuera del horario operativo del consultorio",
        )


def list_bookings(db: Session, start_at: datetime | None, end_at: datetime | None) -> list[Booking]:
    query = select(Booking).where(Booking.deleted_at.is_(None))
    if start_at is not None:
        query = query.where(Booking.end_at > start_at)
    if end_at is not None:
        query = query.where(Booking.start_at < end_at)
    query = query.order_by(Booking.start_at)
    return list(db.execute(query).scalars().all())


def create_booking(db: Session, payload: BookingCreateRequest, actor_id: int) -> Booking:
    _ensure_room_and_professional(db, payload.room_id, payload.professional_id)
    _validate_operating_hours(db, payload.room_id, payload.start_at, payload.end_at)

    now = datetime.utcnow()
    booking = Booking(
        room_id=payload.room_id,
        professional_id=payload.professional_id,
        start_at=payload.start_at,
        end_at=payload.end_at,
        created_at=now,
        updated_at=now,
        created_by=actor_id,
        updated_by=actor_id,
        deleted_at=None,
    )
    db.add(booking)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Conflicto de reserva para el consultorio") from exc
    db.refresh(booking)
    return booking


def create_recurring_bookings(db: Session, payload: BookingRecurringCreateRequest, actor_id: int) -> list[Booking]:
    """Una fila `bookings` por cada fecha del período que coincide con `weekday` (patrón semanal)."""
    _ensure_room_and_professional(db, payload.room_id, payload.professional_id)

    max_days = 400
    if (payload.period_end - payload.period_start).days + 1 > max_days:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"El período no puede superar {max_days} días",
        )

    dates: list[date] = [
        d
        for d in _daterange_inclusive(payload.period_start, payload.period_end)
        if weekday_js_from_date(d) == payload.weekday
    ]
    if not dates:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Ninguna fecha del período coincide con el día de la semana elegido",
        )

    max_occurrences = 200
    if len(dates) > max_occurrences:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Demasiadas ocurrencias (máximo {max_occurrences} por solicitud). Acortá el período.",
        )

    tz = ZoneInfo(settings.business_tz)
    now = datetime.utcnow()
    to_add: list[Booking] = []

    for d in dates:
        start_local = datetime.combine(d, payload.start_time, tzinfo=tz)
        end_local = datetime.combine(d, payload.end_time, tzinfo=tz)
        start_at = start_local.astimezone(UTC)
        end_at = end_local.astimezone(UTC)
        _validate_operating_hours(db, payload.room_id, start_at, end_at)
        to_add.append(
            Booking(
                room_id=payload.room_id,
                professional_id=payload.professional_id,
                start_at=start_at,
                end_at=end_at,
                created_at=now,
                updated_at=now,
                created_by=actor_id,
                updated_by=actor_id,
                deleted_at=None,
            )
        )

    for b in to_add:
        db.add(b)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Alguna ocurrencia choca con otra reserva del mismo consultorio",
        ) from exc

    for b in to_add:
        db.refresh(b)
    return to_add


def update_booking(db: Session, booking_id: int, payload: BookingUpdateRequest, actor_id: int) -> Booking:
    booking = db.execute(select(Booking).where(Booking.id == booking_id, Booking.deleted_at.is_(None))).scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")

    room_id = payload.room_id if payload.room_id is not None else booking.room_id
    professional_id = payload.professional_id if payload.professional_id is not None else booking.professional_id
    start_at = payload.start_at if payload.start_at is not None else booking.start_at
    end_at = payload.end_at if payload.end_at is not None else booking.end_at

    _ensure_room_and_professional(db, room_id, professional_id)
    _validate_operating_hours(db, room_id, start_at, end_at)

    booking.room_id = room_id
    booking.professional_id = professional_id
    booking.start_at = start_at
    booking.end_at = end_at
    booking.updated_at = datetime.utcnow()
    booking.updated_by = actor_id
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Conflicto de reserva para el consultorio") from exc
    db.refresh(booking)
    return booking


def delete_booking(db: Session, booking_id: int, actor_id: int) -> None:
    booking = db.execute(select(Booking).where(Booking.id == booking_id, Booking.deleted_at.is_(None))).scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")
    booking.deleted_at = datetime.utcnow()
    booking.updated_at = datetime.utcnow()
    booking.updated_by = actor_id
    db.commit()
