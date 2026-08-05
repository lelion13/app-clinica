"""locations.id_dominio (vínculo con ocupación)

Revision ID: 0014_locations_id_dominio
Revises: 0013_ocupacion_serial
Create Date: 2026-08-05
"""

from alembic import op
import sqlalchemy as sa

revision = "0014_locations_id_dominio"
down_revision = "0013_ocupacion_serial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("locations", sa.Column("id_dominio", sa.Integer(), nullable=True))
    # Placeholders únicos negativos por fila existente (Q30=A); se corrigen en UI.
    op.execute(sa.text("UPDATE locations SET id_dominio = -id WHERE id_dominio IS NULL"))
    op.alter_column("locations", "id_dominio", existing_type=sa.Integer(), nullable=False)
    op.create_index(
        "uq_locations_id_dominio_active",
        "locations",
        ["id_dominio"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_locations_id_dominio_active", table_name="locations")
    op.drop_column("locations", "id_dominio")
