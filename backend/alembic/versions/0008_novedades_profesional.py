"""Catálogo Novedades: profesionales sync HTTP + retarget FKs

Revision ID: 0008_novedades_profesional
Revises: 0007_fecha_realizacion
Create Date: 2026-07-29
"""

from alembic import op
import sqlalchemy as sa

revision = "0008_novedades_profesional"
down_revision = "0007_fecha_realizacion"
branch_labels = None
depends_on = None


def _drop_fks_on_column(table: str, column: str) -> None:
    op.execute(
        sa.text(
            f"""
            DO $$
            DECLARE r record;
            BEGIN
              FOR r IN (
                SELECT tc.constraint_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                  ON tc.constraint_name = kcu.constraint_name
                 AND tc.table_schema = kcu.table_schema
                WHERE tc.table_schema = current_schema()
                  AND tc.table_name = '{table}'
                  AND tc.constraint_type = 'FOREIGN KEY'
                  AND kcu.column_name = '{column}'
              ) LOOP
                EXECUTE format('ALTER TABLE %I DROP CONSTRAINT %I', '{table}', r.constraint_name);
              END LOOP;
            END $$;
            """
        )
    )


def upgrade() -> None:
    op.create_table(
        "novedades_profesional",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("codprof", sa.String(length=40), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("codprov", sa.String(length=40), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("codprof", name="uq_novedades_profesional_codprof"),
    )

    op.execute("DELETE FROM novedades_asignacion_modulo")
    op.execute("DELETE FROM novedades_novedad")
    op.execute("DELETE FROM novedades_profesional_servicio")

    for table in (
        "novedades_profesional_servicio",
        "novedades_asignacion_modulo",
        "novedades_novedad",
    ):
        _drop_fks_on_column(table, "professional_id")
        op.create_foreign_key(
            f"{table}_professional_id_fkey",
            table,
            "novedades_profesional",
            ["professional_id"],
            ["id"],
        )


def downgrade() -> None:
    op.execute("DELETE FROM novedades_asignacion_modulo")
    op.execute("DELETE FROM novedades_novedad")
    op.execute("DELETE FROM novedades_profesional_servicio")

    for table in (
        "novedades_novedad",
        "novedades_asignacion_modulo",
        "novedades_profesional_servicio",
    ):
        _drop_fks_on_column(table, "professional_id")
        op.create_foreign_key(
            f"{table}_professional_id_fkey",
            table,
            "professionals",
            ["professional_id"],
            ["id"],
        )

    op.drop_table("novedades_profesional")
