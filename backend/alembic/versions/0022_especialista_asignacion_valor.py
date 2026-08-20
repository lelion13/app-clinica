"""es_especialista + valor persistido en asignacion modulo

Revision ID: 0022_especialista_asignacion_valor
Revises: 0021_produccion_tarifa
Create Date: 2026-08-20
"""

from alembic import op
import sqlalchemy as sa

revision = "0022_especialista_asignacion_valor"
down_revision = "0021_produccion_tarifa"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "novedades_profesional",
        sa.Column("es_especialista", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column(
        "novedades_asignacion_modulo",
        sa.Column("valor", sa.Numeric(12, 2), nullable=True),
    )
    op.execute(
        """
        UPDATE novedades_asignacion_modulo a
        SET valor = m.valor
        FROM novedades_modulo m
        WHERE m.id = a.modulo_id AND a.valor IS NULL
        """
    )
    op.alter_column("novedades_asignacion_modulo", "valor", nullable=False)


def downgrade() -> None:
    op.drop_column("novedades_asignacion_modulo", "valor")
    op.drop_column("novedades_profesional", "es_especialista")
