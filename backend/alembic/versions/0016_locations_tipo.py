"""locations.tipo + unique (id_dominio, tipo) activas

Revision ID: 0016_locations_tipo
Revises: 0015_room_id_agenda
Create Date: 2026-08-05
"""

from alembic import op
import sqlalchemy as sa

revision = "0016_locations_tipo"
down_revision = "0015_room_id_agenda"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("locations", sa.Column("tipo", sa.String(length=200), nullable=True))
    # Placeholders únicos por fila existente hasta editar en UI.
    op.execute(sa.text("UPDATE locations SET tipo = 'PENDIENTE-' || id::text WHERE tipo IS NULL OR TRIM(tipo) = ''"))
    op.alter_column("locations", "tipo", existing_type=sa.String(length=200), nullable=False)

    op.drop_index("uq_locations_id_dominio_active", table_name="locations")
    op.create_index(
        "uq_locations_id_dominio_tipo_active",
        "locations",
        ["id_dominio", "tipo"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_locations_id_dominio_tipo_active", table_name="locations")
    op.create_index(
        "uq_locations_id_dominio_active",
        "locations",
        ["id_dominio"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.drop_column("locations", "tipo")
