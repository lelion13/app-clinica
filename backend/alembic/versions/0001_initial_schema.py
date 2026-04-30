"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-04-30
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial_schema"
down_revision = None
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
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.Enum("admin", "operador", name="userrole"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_unique_constraint("uq_users_email", "users", ["email"])
    op.execute("CREATE UNIQUE INDEX uq_users_email_ci ON users (LOWER(email)) WHERE deleted_at IS NULL")

    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False, unique=True),
        *_audit_columns(),
    )

    op.create_table(
        "consulting_rooms",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("locations.id"), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        *_audit_columns(),
    )
    op.create_index("ix_rooms_location", "consulting_rooms", ["location_id"])
    op.execute(
        "CREATE UNIQUE INDEX uq_room_code_per_location ON consulting_rooms (location_id, code) "
        "WHERE deleted_at IS NULL"
    )

    op.create_table(
        "room_operating_hours",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("room_id", sa.Integer(), sa.ForeignKey("consulting_rooms.id"), nullable=False),
        sa.Column("weekday", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        *_audit_columns(),
    )
    op.create_check_constraint("ck_room_operating_weekday", "room_operating_hours", "weekday >= 0 AND weekday <= 6")
    op.create_check_constraint("ck_room_operating_interval", "room_operating_hours", "start_time < end_time")

    op.create_table(
        "professionals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("license_number", sa.String(length=80), nullable=True),
        *_audit_columns(),
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_prof_license ON professionals (license_number) "
        "WHERE license_number IS NOT NULL AND deleted_at IS NULL"
    )

    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("room_id", sa.Integer(), sa.ForeignKey("consulting_rooms.id"), nullable=False),
        sa.Column("professional_id", sa.Integer(), sa.ForeignKey("professionals.id"), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        *_audit_columns(),
    )
    op.create_check_constraint("ck_bookings_interval", "bookings", "start_at < end_at")
    op.create_index("ix_bookings_room_start", "bookings", ["room_id", "start_at"])
    op.create_index("ix_bookings_prof_start", "bookings", ["professional_id", "start_at"])
    op.execute(
        """
        ALTER TABLE bookings
        ADD CONSTRAINT bookings_room_timeslot_excl
        EXCLUDE USING gist (
          room_id WITH =,
          tstzrange(start_at, end_at, '[)') WITH &&
        )
        WHERE (deleted_at IS NULL)
        """
    )


def downgrade() -> None:
    op.drop_table("bookings")
    op.drop_table("professionals")
    op.drop_table("room_operating_hours")
    op.drop_table("consulting_rooms")
    op.drop_table("locations")
    op.execute("DROP INDEX IF EXISTS uq_users_email_ci")
    op.drop_constraint("uq_users_email", "users", type_="unique")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS userrole")
