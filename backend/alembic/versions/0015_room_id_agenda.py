"""Mapeo id_agenda (sync) → consulting_rooms

Revision ID: 0015_room_id_agenda
Revises: 0014_locations_id_dominio
Create Date: 2026-08-05
"""

from alembic import op
import sqlalchemy as sa

revision = "0015_room_id_agenda"
down_revision = "0014_locations_id_dominio"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "consulting_room_id_agenda",
        sa.Column("id_agenda", sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column("room_id", sa.Integer(), sa.ForeignKey("consulting_rooms.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
    )
    op.create_index("ix_consulting_room_id_agenda_room_id", "consulting_room_id_agenda", ["room_id"])


def downgrade() -> None:
    op.drop_index("ix_consulting_room_id_agenda_room_id", table_name="consulting_room_id_agenda")
    op.drop_table("consulting_room_id_agenda")
