"""Ocupación: PK serial — una fila DB por cada fila del endpoint

Revision ID: 0013_ocupacion_serial
Revises: 0012_ocupacion_payload
Create Date: 2026-08-03

Motivo: `id_dato` del endpoint NO es único (miles de filas, pocos id_dato).
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0013_ocupacion_serial"
down_revision = "0012_ocupacion_payload"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("ocupacion_horario_activo")
    op.create_table(
        "ocupacion_horario_activo",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("tipo", sa.String(length=120), nullable=True),
        sa.Column("especialidad_agenda", sa.String(length=200), nullable=True),
        sa.Column("medico", sa.String(length=200), nullable=True),
        sa.Column("fecha_hasta", sa.String(length=40), nullable=True),
        sa.Column("id_dato", sa.String(length=120), nullable=True),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_ocupacion_horario_activo_fecha_hasta", "ocupacion_horario_activo", ["fecha_hasta"])
    op.create_index("ix_ocupacion_horario_activo_id_dato", "ocupacion_horario_activo", ["id_dato"])


def downgrade() -> None:
    op.drop_index("ix_ocupacion_horario_activo_id_dato", table_name="ocupacion_horario_activo")
    op.drop_index("ix_ocupacion_horario_activo_fecha_hasta", table_name="ocupacion_horario_activo")
    op.drop_table("ocupacion_horario_activo")
    op.create_table(
        "ocupacion_horario_activo",
        sa.Column("id_dato", sa.String(length=120), primary_key=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("tipo", sa.String(length=120), nullable=True),
        sa.Column("especialidad_agenda", sa.String(length=200), nullable=True),
        sa.Column("medico", sa.String(length=200), nullable=True),
        sa.Column("fecha_hasta", sa.String(length=40), nullable=True),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_ocupacion_horario_activo_fecha_hasta", "ocupacion_horario_activo", ["fecha_hasta"])
