"""modulo-servicio N:N + valor_hora por servicio

Revision ID: 0006_mod_svc_valor_hora
Revises: 0005_novedades_horas_valor
Create Date: 2026-07-28
"""

from alembic import op
import sqlalchemy as sa

revision = "0006_mod_svc_valor_hora"
down_revision = "0005_novedades_horas_valor"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "novedades_servicio",
        sa.Column("valor_hora", sa.Numeric(12, 2), nullable=False, server_default="0"),
    )
    # Copiar valor global de config (si existe) a todos los servicios.
    op.execute(
        """
        UPDATE novedades_servicio s
        SET valor_hora = COALESCE((SELECT valor_hora FROM novedades_config WHERE id = 1), 0)
        WHERE s.deleted_at IS NULL
        """
    )

    op.create_table(
        "novedades_modulo_servicio",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("modulo_id", sa.Integer(), sa.ForeignKey("novedades_modulo.id"), nullable=False),
        sa.Column("servicio_id", sa.Integer(), sa.ForeignKey("novedades_servicio.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "uq_novedades_modulo_servicio_active",
        "novedades_modulo_servicio",
        ["modulo_id", "servicio_id"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_table("novedades_modulo_servicio")
    op.drop_column("novedades_servicio", "valor_hora")
