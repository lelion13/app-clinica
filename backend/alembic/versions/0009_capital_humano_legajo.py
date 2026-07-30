"""legajo en catálogo Novedades + ajustes Capital Humano

Revision ID: 0009_capital_humano_legajo
Revises: 0008_novedades_profesional
Create Date: 2026-07-30
"""

from alembic import op
import sqlalchemy as sa

revision = "0009_capital_humano_legajo"
down_revision = "0008_novedades_profesional"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("novedades_profesional", sa.Column("legajo", sa.String(length=40), nullable=True))

    op.create_table(
        "novedades_ajuste_capital",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("professional_id", sa.Integer(), sa.ForeignKey("novedades_profesional.id"), nullable=False),
        sa.Column("periodo_id", sa.Integer(), sa.ForeignKey("novedades_periodo.id"), nullable=False),
        sa.Column("servicio_id", sa.Integer(), sa.ForeignKey("novedades_servicio.id"), nullable=True),
        sa.Column("importe", sa.Numeric(12, 2), nullable=False),
        sa.Column("comentario", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_novedades_ajuste_capital_scope",
        "novedades_ajuste_capital",
        ["periodo_id", "professional_id", "servicio_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_novedades_ajuste_capital_scope", table_name="novedades_ajuste_capital")
    op.drop_table("novedades_ajuste_capital")
    op.drop_column("novedades_profesional", "legajo")
