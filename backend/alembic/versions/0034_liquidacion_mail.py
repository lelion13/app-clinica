"""email on novedades_profesional + liquidacion mail lot tables

Revision ID: 0034_liquidacion_mail
Revises: 0033_drop_bookings_weekly
Create Date: 2026-10-19

Note: revision id MUST be <=32 chars (alembic_version.version_num).
"""

from alembic import op
import sqlalchemy as sa

revision = "0034_liquidacion_mail"
down_revision = "0033_drop_bookings_weekly"
branch_labels = None
depends_on = None


def _has_table(table: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return table in insp.get_table_names()


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if table not in insp.get_table_names():
        return False
    return any(c["name"] == column for c in insp.get_columns(table))


def upgrade() -> None:
    if not _has_column("novedades_profesional", "email"):
        op.add_column(
            "novedades_profesional",
            sa.Column("email", sa.String(length=255), nullable=True),
        )

    if not _has_table("novedades_liquidacion_mail_lote"):
        op.create_table(
            "novedades_liquidacion_mail_lote",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("periodo_id", sa.Integer(), sa.ForeignKey("novedades_periodo.id"), nullable=False),
            sa.Column("created_by", sa.Integer(), nullable=True),
            sa.Column("updated_by", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.Column("deleted_at", sa.DateTime(), nullable=True),
            sa.UniqueConstraint("periodo_id", name="uq_liquidacion_mail_lote_periodo"),
        )

    if not _has_table("novedades_liquidacion_mail_item"):
        op.create_table(
            "novedades_liquidacion_mail_item",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "lote_id",
                sa.Integer(),
                sa.ForeignKey("novedades_liquidacion_mail_lote.id"),
                nullable=False,
            ),
            sa.Column(
                "professional_id",
                sa.Integer(),
                sa.ForeignKey("novedades_profesional.id"),
                nullable=False,
            ),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("total_general", sa.Numeric(12, 2), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("error_message", sa.String(length=500), nullable=True),
            sa.Column("sent_at", sa.DateTime(), nullable=True),
            sa.Column("created_by", sa.Integer(), nullable=True),
            sa.Column("updated_by", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.Column("deleted_at", sa.DateTime(), nullable=True),
        )
        op.create_index(
            "ix_liquidacion_mail_item_lote_status",
            "novedades_liquidacion_mail_item",
            ["lote_id", "status"],
        )


def downgrade() -> None:
    if _has_table("novedades_liquidacion_mail_item"):
        op.drop_index("ix_liquidacion_mail_item_lote_status", table_name="novedades_liquidacion_mail_item")
        op.drop_table("novedades_liquidacion_mail_item")
    if _has_table("novedades_liquidacion_mail_lote"):
        op.drop_table("novedades_liquidacion_mail_lote")
    if _has_column("novedades_profesional", "email"):
        op.drop_column("novedades_profesional", "email")
