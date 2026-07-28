"""novedades tipos horas + valor_hora + reshape novedad

Revision ID: 0005_novedades_horas_valor
Revises: 0004_novedades_modulos
Create Date: 2026-07-28
"""

from alembic import op
import sqlalchemy as sa

revision = "0005_novedades_horas_valor"
down_revision = "0004_novedades_modulos"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "novedades_config",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("valor_hora", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute(
        """
        INSERT INTO novedades_config (id, valor_hora, created_at, updated_at)
        VALUES (1, 0, NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
        """
    )

    op.add_column("novedades_novedad", sa.Column("tipo", sa.String(length=40), nullable=True))
    op.add_column("novedades_novedad", sa.Column("horas", sa.Numeric(10, 2), nullable=True))
    op.execute(
        """
        UPDATE novedades_novedad
        SET tipo = 'hora_extra', horas = 1
        WHERE tipo IS NULL
        """
    )
    op.alter_column("novedades_novedad", "tipo", nullable=False)
    op.alter_column("novedades_novedad", "horas", nullable=False)
    op.create_check_constraint(
        "ck_novedades_novedad_tipo",
        "novedades_novedad",
        "tipo IN ('hora_extra', 'hora_extra_por_ausencia')",
    )
    op.create_check_constraint(
        "ck_novedades_novedad_horas",
        "novedades_novedad",
        "horas > 0",
    )

    op.drop_constraint("novedades_novedad_modulo_id_fkey", "novedades_novedad", type_="foreignkey")
    op.drop_column("novedades_novedad", "modulo_id")
    op.drop_column("novedades_novedad", "valor")
    op.drop_column("novedades_novedad", "justificacion")


def downgrade() -> None:
    op.add_column("novedades_novedad", sa.Column("modulo_id", sa.Integer(), nullable=True))
    op.add_column("novedades_novedad", sa.Column("valor", sa.Numeric(12, 2), nullable=True))
    op.add_column("novedades_novedad", sa.Column("justificacion", sa.String(length=1000), nullable=True))
    op.drop_constraint("ck_novedades_novedad_horas", "novedades_novedad", type_="check")
    op.drop_constraint("ck_novedades_novedad_tipo", "novedades_novedad", type_="check")
    op.drop_column("novedades_novedad", "horas")
    op.drop_column("novedades_novedad", "tipo")
    op.drop_table("novedades_config")
