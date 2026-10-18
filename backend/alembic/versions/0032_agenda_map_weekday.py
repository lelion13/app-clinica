"""Map id_agenda+weekday → room (per-day assignment)

Revision ID: 0032_agenda_map_weekday
Revises: 0031_modulo_horas
Create Date: 2026-10-16

Note: revision id MUST be <=32 chars (alembic_version.version_num).
"""

from __future__ import annotations

import json

from alembic import op
import sqlalchemy as sa

revision = "0032_agenda_map_weekday"
down_revision = "0031_modulo_horas"
branch_labels = None
depends_on = None

# Python weekday (Mon=0) → JS weekday (Sun=0), same as agenda_reassign
DIA_TO_PY = {
    "lunes": 0,
    "martes": 1,
    "miercoles": 2,
    "miércoles": 2,
    "jueves": 3,
    "viernes": 4,
    "sabado": 5,
    "sábado": 5,
    "domingo": 6,
}


def _py_to_js(py_wd: int) -> int:
    return (py_wd + 1) % 7


def _weekdays_from_sync(conn) -> dict[int, set[int]]:
    """id_agenda → set of JS weekdays present in ocupacion sync."""
    result: dict[int, set[int]] = {}
    rows = conn.execute(sa.text("SELECT payload FROM ocupacion_horario_activo")).fetchall()
    for (payload,) in rows:
        raw = payload
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except Exception:
                continue
        if not isinstance(raw, dict):
            continue
        id_raw = raw.get("id_agenda")
        if id_raw is None or id_raw == "":
            continue
        try:
            id_agenda = int(id_raw)
        except (TypeError, ValueError):
            continue
        dia = str(raw.get("dia") or "").strip().casefold()
        py_wd = DIA_TO_PY.get(dia)
        if py_wd is None:
            continue
        result.setdefault(id_agenda, set()).add(_py_to_js(py_wd))
    return result


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    cols = {c["name"] for c in insp.get_columns("consulting_room_id_agenda")}
    if "weekday" not in cols:
        op.add_column("consulting_room_id_agenda", sa.Column("weekday", sa.Integer(), nullable=True))

    sync_wds = _weekdays_from_sync(conn)
    legacy = conn.execute(
        sa.text(
            "SELECT id_agenda, room_id, created_at, updated_at, created_by, updated_by "
            "FROM consulting_room_id_agenda WHERE weekday IS NULL"
        )
    ).fetchall()

    if legacy:
        conn.execute(sa.text("DELETE FROM consulting_room_id_agenda WHERE weekday IS NULL"))
        for id_agenda, room_id, created_at, updated_at, created_by, updated_by in legacy:
            weekdays = sorted(sync_wds.get(int(id_agenda)) or set())
            if not weekdays:
                # Sin días en sync: no conservar mapa huérfano
                continue
            for wd in weekdays:
                conn.execute(
                    sa.text(
                        "INSERT INTO consulting_room_id_agenda "
                        "(id_agenda, weekday, room_id, created_at, updated_at, created_by, updated_by) "
                        "VALUES (:id_agenda, :weekday, :room_id, :created_at, :updated_at, :created_by, :updated_by)"
                    ),
                    {
                        "id_agenda": int(id_agenda),
                        "weekday": int(wd),
                        "room_id": int(room_id),
                        "created_at": created_at,
                        "updated_at": updated_at,
                        "created_by": created_by,
                        "updated_by": updated_by,
                    },
                )

    # Filas ya con weekday (re-run) o recién insertadas: NOT NULL + PK compuesta
    conn.execute(sa.text("DELETE FROM consulting_room_id_agenda WHERE weekday IS NULL"))
    op.alter_column("consulting_room_id_agenda", "weekday", existing_type=sa.Integer(), nullable=False)

    pk = insp.get_pk_constraint("consulting_room_id_agenda")
    pk_name = pk.get("name") if pk else None
    pk_cols = list(pk.get("constrained_columns") or []) if pk else []
    if pk_name and pk_cols != ["id_agenda", "weekday"]:
        op.drop_constraint(pk_name, "consulting_room_id_agenda", type_="primary")
        op.create_primary_key(
            "consulting_room_id_agenda_pkey",
            "consulting_room_id_agenda",
            ["id_agenda", "weekday"],
        )


def downgrade() -> None:
    conn = op.get_bind()
    rows = conn.execute(
        sa.text(
            "SELECT DISTINCT ON (id_agenda) id_agenda, room_id, created_at, updated_at, created_by, updated_by "
            "FROM consulting_room_id_agenda ORDER BY id_agenda, weekday"
        )
    ).fetchall()
    op.drop_constraint("consulting_room_id_agenda_pkey", "consulting_room_id_agenda", type_="primary")
    conn.execute(sa.text("DELETE FROM consulting_room_id_agenda"))
    op.drop_column("consulting_room_id_agenda", "weekday")
    for id_agenda, room_id, created_at, updated_at, created_by, updated_by in rows:
        conn.execute(
            sa.text(
                "INSERT INTO consulting_room_id_agenda "
                "(id_agenda, room_id, created_at, updated_at, created_by, updated_by) "
                "VALUES (:id_agenda, :room_id, :created_at, :updated_at, :created_by, :updated_by)"
            ),
            {
                "id_agenda": int(id_agenda),
                "room_id": int(room_id),
                "created_at": created_at,
                "updated_at": updated_at,
                "created_by": created_by,
                "updated_by": updated_by,
            },
        )
    op.create_primary_key("consulting_room_id_agenda_pkey", "consulting_room_id_agenda", ["id_agenda"])
