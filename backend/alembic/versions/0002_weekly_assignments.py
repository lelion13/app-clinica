"""weekly assignments

Revision ID: 0002_weekly_assignments
Revises: 0001_initial_schema
Create Date: 2026-05-04
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_weekly_assignments"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def _audit_columns():
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    ]


def upgrade() -> None:
    op.create_table(
        "room_weekly_assignments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("room_id", sa.Integer(), sa.ForeignKey("consulting_rooms.id"), nullable=False),
        sa.Column("professional_id", sa.Integer(), sa.ForeignKey("professionals.id"), nullable=False),
        sa.Column("weekday", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        *_audit_columns(),
    )
    op.create_check_constraint(
        "ck_room_weekly_assignments_weekday", "room_weekly_assignments", "weekday >= 0 AND weekday <= 6"
    )
    op.create_check_constraint("ck_room_weekly_assignments_interval", "room_weekly_assignments", "start_time < end_time")
    op.create_index("ix_weekly_assignments_room_weekday", "room_weekly_assignments", ["room_id", "weekday"])
    op.create_index(
        "ix_weekly_assignments_prof_weekday", "room_weekly_assignments", ["professional_id", "weekday"]
    )


def downgrade() -> None:
    op.drop_table("room_weekly_assignments")
