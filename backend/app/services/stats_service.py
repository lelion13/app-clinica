"""Estadísticas agregadas (ocupación, rankings) para el dashboard."""

from collections import defaultdict
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.calendar import weekday_js_from_date
from app.core.config import settings
from app.models.consulting_room import ConsultingRoom, RoomOperatingHour
from app.models.professional import Professional
from app.models.weekly_assignment import RoomWeeklyAssignment
from app.schemas.stats import ProfessionalHoursRank, RoomHoursRank, StatsSummaryResponse, WeekdayHoursPoint


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


def _count_weekdays_js_in_period(start_d: date, end_d: date) -> dict[int, int]:
    counts = {i: 0 for i in range(7)}
    for day in _daterange_inclusive(start_d, end_d):
        counts[weekday_js_from_date(day)] += 1
    return counts


def _weekday_js_to_iso(js_weekday: int) -> int:
    """JS day index (0=dom...6=sáb) -> ISO-like chart index (0=lun...6=dom)."""
    return (js_weekday + 6) % 7


_WEEKDAY_LABELS = ("Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom")


def _normalize_specialty_token(value: str) -> str:
    return " ".join(value.strip().lower().split())


def _split_specialties(specialty: str | None) -> set[str]:
    if not specialty:
        return set()
    return {_normalize_specialty_token(token) for token in specialty.split("|") if token.strip()}


def _matching_professional_ids_by_specialty(
    db: Session, professional_ids: set[int], specialty_filters: list[str]
) -> set[int]:
    if not professional_ids or not specialty_filters:
        return set()
    requested = {_normalize_specialty_token(s) for s in specialty_filters if str(s).strip()}
    if not requested:
        return set()
    rows = db.execute(select(Professional.id, Professional.specialty).where(Professional.id.in_(professional_ids))).all()
    matches: set[int] = set()
    for pid, specialty in rows:
        if _split_specialties(specialty).intersection(requested):
            matches.add(pid)
    return matches


def build_stats_summary(
    db: Session,
    start_d: date,
    end_d: date,
    location_ids: list[int],
    room_ids: list[int],
    professional_ids: list[int],
    specialty_filters: list[str],
) -> StatsSummaryResponse:
    if end_d < start_d:
        raise ValueError("Rango de fechas invalido")

    max_days = 400
    if (end_d - start_d).days + 1 > max_days:
        raise ValueError(f"El período no puede superar {max_days} días")

    room_filter_ids = _filtered_room_ids(db, location_ids, room_ids)
    enabled = _compute_enabled_hours(db, room_filter_ids, start_d, end_d)

    booked_hours_filtered: float | None = None
    bookings_count_filtered: int | None = None

    if not room_filter_ids:
        booked = 0.0
        count = 0
        hours_by_weekday: dict[int, float] = defaultdict(float)
        room_totals: dict[int, float] = defaultdict(float)
        prof_totals: dict[int, float] = defaultdict(float)
    else:
        weekday_occurrences = _count_weekdays_js_in_period(start_d, end_d)
        assignments_all = list(
            db.execute(
                select(RoomWeeklyAssignment).where(
                    RoomWeeklyAssignment.deleted_at.is_(None),
                    RoomWeeklyAssignment.room_id.in_(room_filter_ids),
                )
            )
            .scalars()
            .all()
        )
        specialty_professional_ids = _matching_professional_ids_by_specialty(
            db,
            {a.professional_id for a in assignments_all},
            specialty_filters,
        )
        apply_specialty_filter = bool(specialty_filters)
        booked = 0.0
        count = 0
        hours_by_weekday = defaultdict(float)
        room_totals = defaultdict(float)
        prof_totals = defaultdict(float)

        for a in assignments_all:
            if apply_specialty_filter and a.professional_id not in specialty_professional_ids:
                continue
            occ = weekday_occurrences.get(a.weekday, 0)
            if occ <= 0:
                continue
            hours_per_occurrence = (datetime.combine(start_d, a.end_time) - datetime.combine(start_d, a.start_time)).total_seconds() / 3600.0
            seg_hours = hours_per_occurrence * occ
            booked += seg_hours
            count += occ
            iso_wd = _weekday_js_to_iso(a.weekday)
            hours_by_weekday[iso_wd] += seg_hours
            room_totals[a.room_id] += seg_hours
            prof_totals[a.professional_id] += seg_hours

        if professional_ids:
            bh_f = 0.0
            cnt_f = 0
            for a in assignments_all:
                if apply_specialty_filter and a.professional_id not in specialty_professional_ids:
                    continue
                if a.professional_id not in professional_ids:
                    continue
                occ = weekday_occurrences.get(a.weekday, 0)
                if occ <= 0:
                    continue
                hours_per_occurrence = (datetime.combine(start_d, a.end_time) - datetime.combine(start_d, a.start_time)).total_seconds() / 3600.0
                bh_f += hours_per_occurrence * occ
                cnt_f += occ
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
