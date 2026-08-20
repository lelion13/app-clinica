"""es_especialista + valor persistido en asignacion modulo

Revision ID: 0022_especialista_valor
Revises: 0021_produccion_tarifa
Create Date: 2026-08-20

Note: revision id MUST be ≤32 chars (alembic_version.version_num).
"""

from alembic import op
import sqlalchemy as sa

revision = "0022_especialista_valor"
down_revision = "0021_produccion_tarifa"
branch_labels = None
depends_on = None


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    row = bind.execute(
        sa.text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_schema = current_schema() "
            "AND table_name = :t AND column_name = :c"
        ),
        {"t": table, "c": column},
    ).first()
    return row is not None


def upgrade() -> None:
    # Idempotent: a previous attempt may have applied DDL then failed
    # writing version_num because the old revision id exceeded varchar(32).
    if not _has_column("novedades_profesional", "es_especialista"):
        op.add_column(
            "novedades_profesional",
            sa.Column("es_especialista", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        )
    if not _has_column("novedades_asignacion_modulo", "valor"):
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
    if _has_column("novedades_asignacion_modulo", "valor"):
        op.drop_column("novedades_asignacion_modulo", "valor")
    if _has_column("novedades_profesional", "es_especialista"):
        op.drop_column("novedades_profesional", "es_especialista")
