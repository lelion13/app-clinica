"""motivo/obs sin produccion en cargas Novedades

Revision ID: 0017_sin_prod_motivo
Revises: 0016_locations_tipo
Create Date: 2026-08-13
"""

from alembic import op
import sqlalchemy as sa

revision = "0017_sin_prod_motivo"
down_revision = "0016_locations_tipo"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "novedades_asignacion_modulo",
        sa.Column("motivo_sin_produccion", sa.String(length=40), nullable=True),
    )
    op.add_column(
        "novedades_asignacion_modulo",
        sa.Column("observacion_sin_produccion", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "novedades_novedad",
        sa.Column("motivo_sin_produccion", sa.String(length=40), nullable=True),
    )
    op.add_column(
        "novedades_novedad",
        sa.Column("observacion_sin_produccion", sa.String(length=500), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("novedades_novedad", "observacion_sin_produccion")
    op.drop_column("novedades_novedad", "motivo_sin_produccion")
    op.drop_column("novedades_asignacion_modulo", "observacion_sin_produccion")
    op.drop_column("novedades_asignacion_modulo", "motivo_sin_produccion")
