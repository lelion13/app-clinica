"""tarifas produccion valor bonos

Revision ID: 0021_produccion_tarifa
Revises: 0020_servicio_concepto
Create Date: 2026-08-19
"""

from alembic import op
import sqlalchemy as sa

revision = "0021_produccion_tarifa"
down_revision = "0020_servicio_concepto"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "novedades_produccion_tarifa",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("opcion_id", sa.Integer(), sa.ForeignKey("novedades_bono_opcion.id"), nullable=False),
        sa.Column("valor_unitario", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("opcion_id", name="uq_novedades_produccion_tarifa_opcion"),
    )


def downgrade() -> None:
    op.drop_table("novedades_produccion_tarifa")
