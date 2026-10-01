"""servicio especialista flag for plus 20%

Revision ID: 0028_servicio_especialista
Revises: 0027_system_backups
Create Date: 2026-10-01

Note: revision id MUST be <=32 chars (alembic_version.version_num).
"""

from alembic import op
import sqlalchemy as sa

revision = "0028_servicio_especialista"
down_revision = "0027_system_backups"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "novedades_servicio",
        sa.Column("especialista", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.alter_column("novedades_servicio", "especialista", server_default=None)


def downgrade() -> None:
    op.drop_column("novedades_servicio", "especialista")
