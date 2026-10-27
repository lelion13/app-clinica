"""persist valor on novedades_novedad for recalculo

Revision ID: 0035_novedad_valor
Revises: 0034_liquidacion_mail
Create Date: 2026-10-27

Note: revision id MUST be <=32 chars.
"""

from alembic import op
import sqlalchemy as sa

revision = "0035_novedad_valor"
down_revision = "0034_liquidacion_mail"
branch_labels = None
depends_on = None


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if table not in insp.get_table_names():
        return False
    return any(c["name"] == column for c in insp.get_columns(table))


def upgrade() -> None:
    if not _has_column("novedades_novedad", "valor"):
        op.add_column(
            "novedades_novedad",
            sa.Column("valor", sa.Numeric(12, 2), nullable=True),
        )
        op.execute(
            """
            UPDATE novedades_novedad AS n
            SET valor = CASE
                WHEN n.tipo = 'horas_a_descontar' THEN -(n.horas * COALESCE(s.valor_hora, 0))
                ELSE n.horas * COALESCE(s.valor_hora, 0)
            END
            FROM novedades_servicio AS s
            WHERE s.id = n.servicio_id
              AND n.valor IS NULL
            """
        )
        op.execute("UPDATE novedades_novedad SET valor = 0 WHERE valor IS NULL")
        op.alter_column("novedades_novedad", "valor", nullable=False)


def downgrade() -> None:
    if _has_column("novedades_novedad", "valor"):
        op.drop_column("novedades_novedad", "valor")
