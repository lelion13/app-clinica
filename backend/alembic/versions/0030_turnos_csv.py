"""turnos CSV import for Indicadores

Revision ID: 0030_turnos_csv
Revises: 0029_ajuste_mas_menos_lote
Create Date: 2026-10-05

Note: revision id MUST be <=32 chars (alembic_version.version_num).
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0030_turnos_csv"
down_revision = "0029_ajuste_mas_menos_lote"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "turnos_csv_import",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("row_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
    )
    op.create_table(
        "turnos_csv_row",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("import_id", sa.Integer(), sa.ForeignKey("turnos_csv_import.id", ondelete="CASCADE"), nullable=False),
        sa.Column("id_persona", sa.String(64), nullable=True),
        sa.Column("estado", sa.String(16), nullable=False),
        sa.Column("nombre", sa.String(500), nullable=False),
        sa.Column("nombre_norm", sa.String(500), nullable=False, index=True),
        sa.Column("id_agenda", sa.Integer(), nullable=True, index=True),
        sa.Column("fecha_reserva", sa.DateTime(timezone=False), nullable=True),
        sa.Column("fecha_turno", sa.DateTime(timezone=False), nullable=False),
        sa.Column("fecha_presente", sa.DateTime(timezone=False), nullable=True),
        sa.Column("fecha_atencion", sa.DateTime(timezone=False), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.create_index("ix_turnos_csv_row_import_id", "turnos_csv_row", ["import_id"])
    op.create_index("ix_turnos_csv_row_fecha_turno", "turnos_csv_row", ["fecha_turno"])


def downgrade() -> None:
    op.drop_index("ix_turnos_csv_row_fecha_turno", table_name="turnos_csv_row")
    op.drop_index("ix_turnos_csv_row_import_id", table_name="turnos_csv_row")
    op.drop_table("turnos_csv_row")
    op.drop_table("turnos_csv_import")
