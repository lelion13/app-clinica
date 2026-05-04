"""Fechas que entran en un patrón semanal (misma lógica que create_recurring_bookings)."""

from datetime import date, timedelta

from app.core.calendar import weekday_js_from_date


def _dates_matching(period_start: date, period_end: date, weekday_js: int) -> list[date]:
    out: list[date] = []
    d = period_start
    while d <= period_end:
        if weekday_js_from_date(d) == weekday_js:
            out.append(d)
        d += timedelta(days=1)
    return out


def test_two_mondays_in_two_week_window():
    # 2026-01-05 and 2026-01-12 are Mondays; JS Monday = 1
    start = date(2026, 1, 5)
    end = date(2026, 1, 18)
    mondays = _dates_matching(start, end, 1)
    assert mondays == [date(2026, 1, 5), date(2026, 1, 12)]


def test_empty_when_weekday_never_occurs():
    start = date(2026, 1, 6)  # Tue
    end = date(2026, 1, 7)  # Wed
    mondays = _dates_matching(start, end, 1)
    assert mondays == []
