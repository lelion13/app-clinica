"""Calendario / convención de días alineada con el frontend (JavaScript Date.getDay)."""

from datetime import date, datetime


def weekday_js_from_date(d: date) -> int:
    """0=domingo … 6=sábado (misma numeración que `Date.getDay()` y `room_operating_hours.weekday`)."""
    return (d.weekday() + 1) % 7


def weekday_js_from_local_datetime(local_dt: datetime) -> int:
    """Misma numeración que `weekday_js_from_date` pero para un datetime ya en zona local de negocio."""
    return (local_dt.weekday() + 1) % 7
