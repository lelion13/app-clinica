"""descuento_lote_id on novedades_ajuste_capital

Revision ID: 0025_ajuste_descuento_lote
Revises: 0024_practicas_internaciones
Create Date: 2026-09-04

Note: revision id MUST be <=32 chars (alembic_version.version_num).
"""

from alembic import op
import sqlalchemy as sa

revision = "0025_ajuste_descuento_lote"
down_revision = "0024_practicas_internaciones"
branch_labels = None
depends_on = None


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if table not in insp.get_table_names():
        return False
    return any(c["name"] == column for c in insp.get_columns(table))


def upgrade() -> None:
    if not _has_column("novedades_ajuste_capital", "descuento_lote_id"):
        op.add_column(
            "novedades_ajuste_capital",
            sa.Column("descuento_lote_id", sa.String(length=36), nullable=True),
        )
        op.create_index(
            "ix_novedades_ajuste_capital_descuento_lote_id",
            "novedades_ajuste_capital",
            ["descuento_lote_id"],
        )


def downgrade() -> None:
    if _has_column("novedades_ajuste_capital", "descuento_lote_id"):
        op.drop_index("ix_novedades_ajuste_capital_descuento_lote_id", table_name="novedades_ajuste_capital")
        op.drop_column("novedades_ajuste_capital", "descuento_lote_id")
