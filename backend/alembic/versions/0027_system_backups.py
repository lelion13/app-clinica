"""system backup config and logs

Revision ID: 0027_system_backups
Revises: 0026_modulo_tipo_dia
Create Date: 2026-09-14

Note: revision id MUST be <=32 chars (alembic_version.version_num).
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0027_system_backups"
down_revision = "0026_modulo_tipo_dia"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "system_backup_config",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("schedule_type", sa.String(length=32), nullable=False, server_default="daily"),
        sa.Column("schedule_time", sa.String(length=8), nullable=False, server_default="03:00"),
        sa.Column("schedule_day_of_week", sa.Integer(), nullable=True),
        sa.Column("s3_endpoint_url", sa.String(length=512), nullable=True),
        sa.Column("s3_bucket_name", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("s3_region_name", sa.String(length=64), nullable=False, server_default="auto"),
        sa.Column("s3_access_key_id", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("s3_secret_access_key", sa.String(length=512), nullable=False, server_default=""),
        sa.Column("s3_prefix", sa.String(length=255), nullable=False, server_default="clinica-backups/"),
        sa.Column("retention_count", sa.Integer(), nullable=False, server_default="15"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.execute(
        sa.text(
            """
            INSERT INTO system_backup_config (
                id, enabled, schedule_type, schedule_time, s3_bucket_name, s3_region_name,
                s3_access_key_id, s3_secret_access_key, s3_prefix, retention_count
            ) VALUES (
                1, false, 'daily', '03:00', '', 'auto', '', '', 'clinica-backups/', 15
            )
            ON CONFLICT (id) DO NOTHING
            """
        )
    )

    op.create_table(
        "system_backup_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("trigger_type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("storage_key", sa.String(length=512), nullable=True),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_system_backup_logs_started_at", "system_backup_logs", ["started_at"])


def downgrade() -> None:
    op.drop_index("ix_system_backup_logs_started_at", table_name="system_backup_logs")
    op.drop_table("system_backup_logs")
    op.drop_table("system_backup_config")
