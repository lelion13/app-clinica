"""practicas e internaciones snapshot tables

Revision ID: 0024_practicas_internaciones
Revises: 0023_password_reset
Create Date: 2026-08-28

Note: revision id MUST be <=32 chars (alembic_version.version_num).
"""

from alembic import op
import sqlalchemy as sa

revision = "0024_practicas_internaciones"
down_revision = "0023_password_reset"
branch_labels = None
depends_on = None


def _has_table(table: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return table in insp.get_table_names()


def upgrade() -> None:
    if not _has_table("novedades_practica_cantidad"):
        op.create_table(
            "novedades_practica_cantidad",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("periodo_id", sa.Integer(), sa.ForeignKey("novedades_periodo.id"), nullable=False),
            sa.Column("professional_id", sa.Integer(), sa.ForeignKey("novedades_profesional.id"), nullable=False),
            sa.Column("centro", sa.String(length=80), nullable=False),
            sa.Column("servicio", sa.String(length=80), nullable=False),
            sa.Column("cantidad", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint(
                "periodo_id",
                "professional_id",
                "centro",
                "servicio",
                name="uq_novedades_practica_cantidad_scope",
            ),
        )
        op.create_index(
            "ix_novedades_practica_cantidad_periodo",
            "novedades_practica_cantidad",
            ["periodo_id"],
        )

    if not _has_table("novedades_internacion_cantidad"):
        op.create_table(
            "novedades_internacion_cantidad",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("periodo_id", sa.Integer(), sa.ForeignKey("novedades_periodo.id"), nullable=False),
            sa.Column("professional_id", sa.Integer(), sa.ForeignKey("novedades_profesional.id"), nullable=False),
            sa.Column("sucursal", sa.String(length=80), nullable=False),
            sa.Column("cantidad", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint(
                "periodo_id",
                "professional_id",
                "sucursal",
                name="uq_novedades_internacion_cantidad_scope",
            ),
        )
        op.create_index(
            "ix_novedades_internacion_cantidad_periodo",
            "novedades_internacion_cantidad",
            ["periodo_id"],
        )


def downgrade() -> None:
    if _has_table("novedades_internacion_cantidad"):
        op.drop_index("ix_novedades_internacion_cantidad_periodo", table_name="novedades_internacion_cantidad")
        op.drop_table("novedades_internacion_cantidad")
    if _has_table("novedades_practica_cantidad"):
        op.drop_index("ix_novedades_practica_cantidad_periodo", table_name="novedades_practica_cantidad")
        op.drop_table("novedades_practica_cantidad")
