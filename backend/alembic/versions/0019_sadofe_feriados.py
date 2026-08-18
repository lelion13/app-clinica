"""sadofe on modulo, feriados table, horas_a_descontar tipo

Revision ID: 0019_sadofe_feriados
Revises: 0018_modulo_produccion
Create Date: 2026-08-16
"""

from alembic import op
import sqlalchemy as sa

revision = "0019_sadofe_feriados"
down_revision = "0018_modulo_produccion"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "novedades_modulo",
        sa.Column("sadofe", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_table(
        "novedades_feriado",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("nombre", sa.String(length=200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "uq_novedades_feriado_fecha_active",
        "novedades_feriado",
        ["fecha"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.drop_constraint("ck_novedades_novedad_tipo", "novedades_novedad", type_="check")
    op.create_check_constraint(
        "ck_novedades_novedad_tipo",
        "novedades_novedad",
        "tipo IN ('hora_extra', 'hora_extra_por_ausencia', 'horas_a_descontar')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_novedades_novedad_tipo", "novedades_novedad", type_="check")
    op.create_check_constraint(
        "ck_novedades_novedad_tipo",
        "novedades_novedad",
        "tipo IN ('hora_extra', 'hora_extra_por_ausencia')",
    )
    op.drop_index("uq_novedades_feriado_fecha_active", table_name="novedades_feriado")
    op.drop_table("novedades_feriado")
    op.drop_column("novedades_modulo", "sadofe")
