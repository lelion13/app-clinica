"""Estadísticas agregadas (ocupación, rankings) para el dashboard."""

from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.calendar import weekday_js_from_date
from app.core.config import settings
from app.models.booking import Booking
from app.models.consulting_room import ConsultingRoom, RoomOperatingHour
from app.models.professional import Professional
from app.schemas.stats import (
    ProfessionalHoursRank,
    RoomHoursRank,
    StatsSummaryResponse,
    WeekdayHoursPoint,
)


def _daterange_inclusive(start: date, end: date):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def _filtered_room_ids(db: Session, location_ids: list[int], room_ids: list[int]) -> list[int]:
    q = select(ConsultingRoom.id).where(ConsultingRoom.deleted_at.is_(None))
    if location_ids:
        q = q.where(ConsultingRoom.location_id.in_(location_ids))
    if room_ids:
        q = q.where(ConsultingRoom.id.in_(room_ids))
    return list(db.execute(q).scalars().all())


def _compute_enabled_hours(db: Session, room_ids: list[int], start_d: date, end_d: date) -> float:
    if not room_ids:
        return 0.0
    tz = ZoneInfo(settings.business_tz)
    total_seconds = 0.0
    for day in _daterange_inclusive(start_d, end_d):
        js_wd = weekday_js_from_date(day)
        rows = db.execute(
            select(RoomOperatingHour.start_time, RoomOperatingHour.end_time).where(
                RoomOperatingHour.room_id.in_(room_ids),
                RoomOperatingHour.weekday == js_wd,
                RoomOperatingHour.deleted_at.is_(None),
            )
        ).all()
        for st, et in rows:
            start_dt = datetime.combine(day, st, tzinfo=tz)
            end_dt = datetime.combine(day, et, tzinfo=tz)
            total_seconds += (end_dt - start_dt).total_seconds()
    return total_seconds / 3600.0


def _period_bounds_utc(start_d: date, end_d: date) -> tuple[datetime, datetime]:
    """[start_d 00:00, end_d+1 00:00) en zona de negocio, devuelto como UTC aware."""
    tz = ZoneInfo(settings.business_tz)
    start_local = datetime.combine(start_d, datetime.min.time(), tzinfo=tz)
    end_next_local = datetime.combine(end_d + timedelta(days=1), datetime.min.time(), tzinfo=tz)
    return start_local.astimezone(UTC), end_next_local.astimezone(UTC)


def _aggregate_bookings_for_period(
    bookings: list[Booking],
    range_start_utc: datetime,
    range_end_excl_utc: datetime,
    tz: ZoneInfo,
) -> tuple[float, int, dict[int, float], dict[int, float], dict[int, float]]:
    """Horas solapadas con el período; weekday en índice ISO (lun=0 … dom=6)."""
    booked = 0.0
    hours_by_weekday: dict[int, float] = defaultdict(float)
    room_totals: dict[int, float] = defaultdict(float)
    prof_totals: dict[int, float] = defaultdict(float)
    overlap_count = 0
    for b in bookings:
        overlap_start = max(b.start_at, range_start_utc)
        overlap_end = min(b.end_at, range_end_excl_utc)
        if overlap_start >= overlap_end:
            continue
        overlap_count += 1
        seg_hours = (overlap_end - overlap_start).total_seconds() / 3600.0
        booked += seg_hours
        wd = overlap_start.astimezone(tz).weekday()
        hours_by_weekday[wd] += seg_hours
        room_totals[b.room_id] += seg_hours
        prof_totals[b.professional_id] += seg_hours
    return booked, overlap_count, hours_by_weekday, room_totals, prof_totals


_WEEKDAY_LABELS = ("Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom")


def build_stats_summary(
    db: Session,
    start_d: date,
    end_d: date,
    location_ids: list[int],
    room_ids: list[int],
    professional_ids: list[int],
) -> StatsSummaryResponse:
    if end_d < start_d:
        raise ValueError("Rango de fechas invalido")

    max_days = 400
    if (end_d - start_d).days + 1 > max_days:
        raise ValueError(f"El período no puede superar {max_days} días")

    room_filter_ids = _filtered_room_ids(db, location_ids, room_ids)
    enabled = _compute_enabled_hours(db, room_filter_ids, start_d, end_d)

    range_start_utc, range_end_excl_utc = _period_bounds_utc(start_d, end_d)
    tz = ZoneInfo(settings.business_tz)

    booked_hours_filtered: float | None = None
    bookings_count_filtered: int | None = None

    if not room_filter_ids:
        booked = 0.0
        count = 0
        hours_by_weekday: dict[int, float] = defaultdict(float)
        room_totals: dict[int, float] = defaultdict(float)
        prof_totals: dict[int, float] = defaultdict(float)
    else:
        q_all = select(Booking).where(
            Booking.deleted_at.is_(None),
            Booking.room_id.in_(room_filter_ids),
            Booking.start_at < range_end_excl_utc,
            Booking.end_at > range_start_utc,
        )
        bookings_all = list(db.execute(q_all).scalars().all())
        booked, count, hours_by_weekday, room_totals, prof_totals = _aggregate_bookings_for_period(
            bookings_all, range_start_utc, range_end_excl_utc, tz
        )

        if professional_ids:
            q_f = select(Booking).where(
                Booking.deleted_at.is_(None),
                Booking.room_id.in_(room_filter_ids),
                Booking.start_at < range_end_excl_utc,
                Booking.end_at > range_start_utc,
                Booking.professional_id.in_(professional_ids),
            )
            bookings_f = list(db.execute(q_f).scalars().all())
            bh_f, cnt_f, _, _, _ = _aggregate_bookings_for_period(
                bookings_f, range_start_utc, range_end_excl_utc, tz
            )
            booked_hours_filtered = round(bh_f, 2)
            bookings_count_filtered = cnt_f

    occupancy = (booked / enabled * 100.0) if enabled > 0 else 0.0
    pie_occ = min(booked, enabled) if enabled > 0 else 0.0
    pie_free = max(0.0, enabled - pie_occ)

    weekday_points: list[WeekdayHoursPoint] = []
    for i in range(7):
        weekday_points.append(
            WeekdayHoursPoint(
                weekday_index=i,
                label=_WEEKDAY_LABELS[i],
                booked_hours=round(hours_by_weekday.get(i, 0.0), 2),
            )
        )

    top_rooms: list[RoomHoursRank] = []
    if room_totals:
        sorted_rooms = sorted(room_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        room_codes = {
            r.id: r.code
            for r in db.execute(
                select(ConsultingRoom).where(ConsultingRoom.id.in_([x[0] for x in sorted_rooms]))
            ).scalars().all()
        }
        for rid, hrs in sorted_rooms:
            top_rooms.append(
                RoomHoursRank(room_id=rid, room_code=room_codes.get(rid, str(rid)), booked_hours=round(hrs, 2))
            )

    top_professionals: list[ProfessionalHoursRank] = []
    if prof_totals:
        sorted_prof = sorted(prof_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        names = {
            p.id: p.full_name
            for p in db.execute(
                select(Professional).where(Professional.id.in_([x[0] for x in sorted_prof]))
            ).scalars().all()
        }
        for pid, hrs in sorted_prof:
            top_professionals.append(
                ProfessionalHoursRank(
                    professional_id=pid,
                    full_name=names.get(pid, str(pid)),
                    booked_hours=round(hrs, 2),
                )
            )

    return StatsSummaryResponse(
        period_start=start_d,
        period_end=end_d,
        enabled_hours=round(enabled, 2),
        booked_hours=round(booked, 2),
        occupancy_rate_percent=round(occupancy, 2),
        bookings_count=count,
        booked_hours_filtered=booked_hours_filtered,
        bookings_count_filtered=bookings_count_filtered,
        pie_occupied_hours=round(pie_occ, 2),
        pie_free_hours=round(pie_free, 2),
        hours_by_weekday=weekday_points,
        top_rooms=top_rooms,
        top_professionals=top_professionals,
    )
