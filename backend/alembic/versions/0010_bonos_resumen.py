"""Snapshot bonos resumen para Capital Humano

Revision ID: 0010_bonos_resumen
Revises: 0009_capital_humano_legajo
Create Date: 2026-07-31
"""

from alembic import op
import sqlalchemy as sa

revision = "0010_bonos_resumen"
down_revision = "0009_capital_humano_legajo"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "novedades_bono_opcion",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("centro", sa.String(length=80), nullable=False),
        sa.Column("servicio", sa.String(length=80), nullable=False),
        sa.Column("semana", sa.String(length=80), nullable=False),
        sa.Column("horario", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("centro", "servicio", "semana", "horario", name="uq_novedades_bono_opcion"),
    )

    op.create_table(
        "novedades_bono_cantidad",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("periodo_id", sa.Integer(), sa.ForeignKey("novedades_periodo.id"), nullable=False),
        sa.Column("professional_id", sa.Integer(), sa.ForeignKey("novedades_profesional.id"), nullable=False),
        sa.Column("opcion_id", sa.Integer(), sa.ForeignKey("novedades_bono_opcion.id"), nullable=False),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint(
            "periodo_id",
            "professional_id",
            "opcion_id",
            name="uq_novedades_bono_cantidad_scope",
        ),
    )
    op.create_index(
        "ix_novedades_bono_cantidad_periodo",
        "novedades_bono_cantidad",
        ["periodo_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_novedades_bono_cantidad_periodo", table_name="novedades_bono_cantidad")
    op.drop_table("novedades_bono_cantidad")
    op.drop_table("novedades_bono_opcion")
