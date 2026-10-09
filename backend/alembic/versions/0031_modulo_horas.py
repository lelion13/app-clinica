"""horas on novedades_modulo catalog

Revision ID: 0031_modulo_horas
Revises: 0030_turnos_csv
Create Date: 2026-10-09

Note: revision id MUST be <=32 chars (alembic_version.version_num).
"""

from alembic import op
import sqlalchemy as sa

revision = "0031_modulo_horas"
down_revision = "0030_turnos_csv"
branch_labels = None
depends_on = None


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if table not in insp.get_table_names():
        return False
    return any(c["name"] == column for c in insp.get_columns(table))


def upgrade() -> None:
    if not _has_column("novedades_modulo", "horas"):
        op.add_column(
            "novedades_modulo",
            sa.Column("horas", sa.Integer(), nullable=True),
        )


def downgrade() -> None:
    if _has_column("novedades_modulo", "horas"):
        op.drop_column("novedades_modulo", "horas")
