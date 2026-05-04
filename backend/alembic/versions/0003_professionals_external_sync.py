"""professionals external sync fields

Revision ID: 0003_professionals_external_sync
Revises: 0002_weekly_assignments
Create Date: 2026-05-04
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_professionals_external_sync"
down_revision = "0002_weekly_assignments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("professionals", sa.Column("external_document", sa.String(length=40), nullable=True))
    op.add_column("professionals", sa.Column("email", sa.String(length=255), nullable=True))
    op.add_column("professionals", sa.Column("profession", sa.String(length=80), nullable=True))
    op.add_column("professionals", sa.Column("license_type", sa.String(length=80), nullable=True))
    op.add_column("professionals", sa.Column("specialty", sa.String(length=500), nullable=True))
    op.add_column("professionals", sa.Column("external_status", sa.String(length=8), nullable=True))
    op.add_column(
        "professionals",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_prof_external_document ON professionals (external_document) "
        "WHERE external_document IS NOT NULL AND deleted_at IS NULL"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_prof_external_document")
    op.drop_column("professionals", "is_active")
    op.drop_column("professionals", "external_status")
    op.drop_column("professionals", "specialty")
    op.drop_column("professionals", "license_type")
    op.drop_column("professionals", "profession")
    op.drop_column("professionals", "email")
    op.drop_column("professionals", "external_document")
