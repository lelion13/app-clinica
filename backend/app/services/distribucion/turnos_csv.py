"""Import + stats for turnos CSV (Indicadores ocupación)."""

from __future__ import annotations

import csv
import io
import re
import unicodedata
from collections import defaultdict
from datetime import date, datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.consulting_room import ConsultingRoom
from app.models.ocupacion import OcupacionHorarioActivo
from app.models.turnos_csv import TurnosCsvImport, TurnosCsvRow
from app.schemas.distribucion import (
    TurnosCsvImportInfo,
    TurnosCsvImportResponse,
    TurnosCsvStatsResponse,
    TurnosCsvUnmatchedItem,
)
from app.services import room_agenda_map as room_agenda_map_service
from app.services.distribucion import agenda_ocupacion as agenda_svc
from app.services.distribucion import indicadores_ocupacion as ind_svc

ESTADOS_TURNOS = frozenset({"AT", "AU"})
ESTADO_AUSENTE = "AU"
ESTADO_ATENDIDO = "AT"

_DATE_RE = re.compile(
    r"^(\d{4})-(\d{1,2})-(\d{1,2})(?:[,\s]+(\d{1,2}):(\d{2})(?::(\d{2}))?)?"
)


def normalize_nombre(value: str | None) -> str:
    text = (value or "").strip()
    if not text:
        return ""
    decomposed = unicodedata.normalize("NFD", text)
    without_marks = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    collapsed = re.sub(r"\s+", " ", without_marks).strip()
    return collapsed.casefold()


def parse_csv_datetime(raw: str | None) -> datetime | None:
    text = (raw or "").strip().strip('"')
    if not text:
        return None
    m = _DATE_RE.match(text)
    if not m:
        # try ISO-ish
        try:
            return datetime.fromisoformat(text.replace(",", " ").replace("  ", " ").strip())
        except ValueError:
            return None
    year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
    hour = int(m.group(4) or 0)
    minute = int(m.group(5) or 0)
    second = int(m.group(6) or 0)
    try:
        return datetime(year, month, day, hour, minute, second)
    except ValueError:
        return None


def _sync_nombre_index(db: Session) -> dict[str, list[int]]:
    """nombre_norm → sorted unique id_agenda list."""
    rows = db.execute(select(OcupacionHorarioActivo)).scalars().all()
    index: dict[str, set[int]] = defaultdict(set)
    for row in rows:
        raw = row.payload if isinstance(row.payload, dict) else {}
        nombre = agenda_svc._as_str(raw.get("nombre_agenda"))
        id_agenda = raw.get("id_agenda")
        try:
            id_int = int(id_agenda) if id_agenda is not None and id_agenda != "" else None
        except (TypeError, ValueError):
            id_int = None
        key = normalize_nombre(nombre)
        if not key or id_int is None:
            continue
        index[key].add(id_int)
    return {k: sorted(v) for k, v in index.items()}


def _agenda_attrs(db: Session) -> dict[int, dict[str, Any]]:
    """id_agenda → especialidad, medico_payload, room_id, location_id (best-effort from any sync row)."""
    rows = db.execute(select(OcupacionHorarioActivo)).scalars().all()
    agenda_rooms = room_agenda_map_service.agenda_to_room_map(db)
    rooms = list(
        db.execute(select(ConsultingRoom).where(ConsultingRoom.deleted_at.is_(None))).scalars().all()
    )
    room_loc = {r.id: r.location_id for r in rooms}
    out: dict[int, dict[str, Any]] = {}
    for row in rows:
        fields = agenda_svc._payload_fields(row)
        id_ag = fields["id_agenda"]
        if id_ag is None:
            continue
        if id_ag in out:
            continue
        rid = agenda_rooms.get(id_ag)
        out[id_ag] = {
            "especialidad": fields["especialidad"],
            "medico_payload": fields["medico_payload"],
            "room_id": rid,
            "location_id": room_loc.get(rid) if rid is not None else None,
        }
    return out


def import_turnos_csv(
    db: Session,
    *,
    filename: str,
    content: bytes,
    actor_id: int | None,
) -> TurnosCsvImportResponse:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="CSV vacío o sin headers")

    # Normalize header keys (strip)
    def row_get(row: dict, *keys: str) -> str:
        for k in keys:
            for hk, hv in row.items():
                if (hk or "").strip().casefold() == k.casefold():
                    return "" if hv is None else str(hv)
        return ""

    sync_index = _sync_nombre_index(db)
    unmatched: list[TurnosCsvUnmatchedItem] = []
    parsed: list[dict[str, Any]] = []
    dates: list[date] = []

    for i, row in enumerate(reader, start=2):  # 1=header
        nombre = row_get(row, "Nombre").strip().strip('"')
        estado = row_get(row, "Estado Turno").strip().upper()
        fecha_turno = parse_csv_datetime(row_get(row, "Fecha Turno"))
        if not nombre or fecha_turno is None:
            continue
        nombre_norm = normalize_nombre(nombre)
        ids = sync_index.get(nombre_norm) or []
        if not ids:
            unmatched.append(TurnosCsvUnmatchedItem(row=i, nombre=nombre))
            continue
        parsed.append(
            {
                "id_persona": row_get(row, "ID Persona").strip() or None,
                "estado": estado or "?",
                "nombre": nombre,
                "nombre_norm": nombre_norm,
                "id_agenda": ids[0],
                "fecha_reserva": parse_csv_datetime(row_get(row, "Fecha Reserva")),
                "fecha_turno": fecha_turno,
                "fecha_presente": parse_csv_datetime(row_get(row, "Fecha Presente")),
                "fecha_atencion": parse_csv_datetime(row_get(row, "Fecha Atencion", "Fecha Atención")),
                "payload": {
                    "tipo_reserva": row_get(row, "Tipo Reserva Turno") or None,
                    "tipo_turno": row_get(row, "Tipo Turno") or None,
                    "area": row_get(row, "Area Jerarquica", "Área Jerarquica") or None,
                    "cobertura": row_get(row, "Cobertura") or None,
                },
            }
        )
        dates.append(fecha_turno.date())

    if unmatched:
        # unique by nombre but keep row refs (cap list)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": f"{len(unmatched)} fila(s) sin match de agenda por Nombre",
                "code": "unmatched_nombres",
                "unmatched": [u.model_dump() for u in unmatched[:200]],
                "unmatched_count": len(unmatched),
                "matched_preview": len(parsed),
            },
        )

    if not parsed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No hay filas válidas con Nombre y Fecha Turno",
        )

    period_start = min(dates)
    period_end = max(dates)
    now = datetime.utcnow()
    imp = TurnosCsvImport(
        filename=(filename or "turnos.csv")[:255],
        period_start=period_start,
        period_end=period_end,
        row_count=len(parsed),
        created_at=now,
        created_by=actor_id,
    )
    db.add(imp)
    db.flush()

    for item in parsed:
        db.add(
            TurnosCsvRow(
                import_id=imp.id,
                id_persona=item["id_persona"],
                estado=item["estado"],
                nombre=item["nombre"][:500],
                nombre_norm=item["nombre_norm"][:500],
                id_agenda=item["id_agenda"],
                fecha_reserva=item["fecha_reserva"],
                fecha_turno=item["fecha_turno"],
                fecha_presente=item["fecha_presente"],
                fecha_atencion=item["fecha_atencion"],
                payload=item["payload"],
            )
        )
    db.commit()
    db.refresh(imp)

    return TurnosCsvImportResponse(
        id=imp.id,
        filename=imp.filename,
        period_start=imp.period_start.isoformat(),
        period_end=imp.period_end.isoformat(),
        row_count=imp.row_count,
    )


def _period_bounds(
    period: str,
    date_str: str | None,
    month_str: str | None,
) -> tuple[datetime, datetime]:
    period_norm = (period or "day").strip().lower()
    if period_norm == "day":
        day = ind_svc._parse_date(date_str)
        start = datetime(day.year, day.month, day.day, 0, 0, 0)
        end = datetime(day.year, day.month, day.day, 23, 59, 59)
        return start, end
    year, month = ind_svc._parse_month(month_str)
    import calendar

    last = calendar.monthrange(year, month)[1]
    start = datetime(year, month, 1, 0, 0, 0)
    end = datetime(year, month, last, 23, 59, 59)
    return start, end


def _passes_filters(
    attrs: dict[str, Any] | None,
    *,
    location_id: int | None,
    room_id: int | None,
    especialidad: str | None,
    medico: str | None,
) -> bool:
    if location_id is None and room_id is None and not especialidad and not medico:
        return True
    if attrs is None:
        return False
    if location_id is not None and attrs.get("location_id") != location_id:
        return False
    if room_id is not None and attrs.get("room_id") != room_id:
        return False
    if especialidad and not agenda_svc._match_multi(attrs.get("especialidad"), [especialidad]):
        return False
    if medico and not agenda_svc._match_medico_payload(attrs.get("medico_payload"), [medico]):
        return False
    return True


def compute_turnos_stats(
    db: Session,
    *,
    period: str = "day",
    date_str: str | None = None,
    month_str: str | None = None,
    location_id: int | None = None,
    room_id: int | None = None,
    especialidad: str | None = None,
    medico: str | None = None,
) -> TurnosCsvStatsResponse:
    start, end = _period_bounds(period, date_str, month_str)
    attrs_by_agenda = _agenda_attrs(db)

    rows = list(
        db.execute(
            select(TurnosCsvRow).where(
                TurnosCsvRow.fecha_turno >= start,
                TurnosCsvRow.fecha_turno <= end,
            )
        )
        .scalars()
        .all()
    )

    turnos = 0
    ausentes = 0
    wait_days: list[float] = []
    presente_mins: list[float] = []

    for row in rows:
        if row.estado not in ESTADOS_TURNOS:
            continue
        attrs = attrs_by_agenda.get(row.id_agenda) if row.id_agenda is not None else None
        if not _passes_filters(
            attrs,
            location_id=location_id,
            room_id=room_id,
            especialidad=especialidad,
            medico=medico,
        ):
            continue
        turnos += 1
        if row.estado == ESTADO_AUSENTE:
            ausentes += 1
        if row.estado == ESTADO_ATENDIDO:
            if row.fecha_reserva and row.fecha_turno:
                wait_days.append((row.fecha_turno.date() - row.fecha_reserva.date()).days)
            if row.fecha_presente and row.fecha_atencion and row.fecha_atencion >= row.fecha_presente:
                presente_mins.append((row.fecha_atencion - row.fecha_presente).total_seconds() / 60.0)

    ausentismo = round((ausentes / turnos) * 100, 2) if turnos > 0 else None
    avg_wait = round(sum(wait_days) / len(wait_days), 2) if wait_days else None
    avg_presente = round(sum(presente_mins) / len(presente_mins), 2) if presente_mins else None

    imports = list(db.execute(select(TurnosCsvImport).order_by(TurnosCsvImport.id.desc())).scalars().all())
    import_infos = [
        TurnosCsvImportInfo(
            id=i.id,
            filename=i.filename,
            period_start=i.period_start.isoformat(),
            period_end=i.period_end.isoformat(),
            rows=i.row_count,
        )
        for i in imports[:20]
    ]

    return TurnosCsvStatsResponse(
        turnos=turnos,
        ausentes=ausentes,
        ausentismo_percent=ausentismo,
        avg_presente_atendido_minutes=avg_presente,
        avg_espera_dias=avg_wait,
        imports=import_infos,
    )
