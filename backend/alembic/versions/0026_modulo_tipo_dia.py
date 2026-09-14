"""Replace novedades_modulo.sadofe with tipo_dia

Revision ID: 0026_modulo_tipo_dia
Revises: 0025_ajuste_descuento_lote
Create Date: 2026-09-14

Note: revision id MUST be <=32 chars (alembic_version.version_num).
"""

from alembic import op
import sqlalchemy as sa

revision = "0026_modulo_tipo_dia"
down_revision = "0025_ajuste_descuento_lote"
branch_labels = None
depends_on = None


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if table not in insp.get_table_names():
        return False
    return any(c["name"] == column for c in insp.get_columns(table))


def _has_check(name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return any(c["name"] == name for c in insp.get_check_constraints("novedades_modulo"))


def upgrade() -> None:
    if not _has_column("novedades_modulo", "tipo_dia"):
        op.add_column(
            "novedades_modulo",
            sa.Column("tipo_dia", sa.String(length=20), nullable=False, server_default="semana"),
        )

    if _has_column("novedades_modulo", "sadofe"):
        op.execute(
            sa.text(
                """
                UPDATE novedades_modulo
                SET tipo_dia = CASE WHEN sadofe IS TRUE THEN 'sadofe' ELSE 'semana' END
                """
            )
        )
        op.drop_column("novedades_modulo", "sadofe")

    if not _has_check("ck_novedades_modulo_tipo_dia"):
        op.create_check_constraint(
            "ck_novedades_modulo_tipo_dia",
            "novedades_modulo",
            "tipo_dia IN ('semana', 'sadofe', 'valor_unico')",
        )


def downgrade() -> None:
    if _has_check("ck_novedades_modulo_tipo_dia"):
        op.drop_constraint("ck_novedades_modulo_tipo_dia", "novedades_modulo", type_="check")

    if not _has_column("novedades_modulo", "sadofe"):
        op.add_column(
            "novedades_modulo",
            sa.Column("sadofe", sa.Boolean(), nullable=False, server_default=sa.false()),
        )

    if _has_column("novedades_modulo", "tipo_dia"):
        op.execute(
            sa.text(
                """
                UPDATE novedades_modulo
                SET sadofe = CASE WHEN tipo_dia = 'sadofe' THEN TRUE ELSE FALSE END
                """
            )
        )
        op.drop_column("novedades_modulo", "tipo_dia")
