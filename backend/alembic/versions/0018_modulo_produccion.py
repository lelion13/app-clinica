"""produccion flag on novedades_modulo

Revision ID: 0018_modulo_produccion
Revises: 0017_sin_prod_motivo
Create Date: 2026-08-13
"""

from alembic import op
import sqlalchemy as sa

revision = "0018_modulo_produccion"
down_revision = "0017_sin_prod_motivo"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "novedades_modulo",
        sa.Column("produccion", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("novedades_modulo", "produccion")
