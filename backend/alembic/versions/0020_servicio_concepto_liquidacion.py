"""concepto_liquidacion on novedades_servicio

Revision ID: 0020_servicio_concepto
Revises: 0019_sadofe_feriados
Create Date: 2026-08-17
"""

from alembic import op
import sqlalchemy as sa

revision = "0020_servicio_concepto"
down_revision = "0019_sadofe_feriados"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "novedades_servicio",
        sa.Column("concepto_liquidacion", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("novedades_servicio", "concepto_liquidacion")
