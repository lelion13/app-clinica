"""Regression: weekday index must match JS Date.getDay() / dashboard operating-hour select."""

from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.calendar import weekday_js_from_local_datetime


def test_weekday_js_monday():
    dt = datetime(2025, 5, 5, 10, 0, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
    assert dt.weekday() == 0  # Python Monday
    assert weekday_js_from_local_datetime(dt) == 1  # JavaScript Monday


def test_weekday_js_sunday():
    dt = datetime(2025, 5, 4, 10, 0, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
    assert dt.weekday() == 6  # Python Sunday
    assert weekday_js_from_local_datetime(dt) == 0  # JavaScript Sunday
