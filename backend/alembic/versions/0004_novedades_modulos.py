"""novedades domain + userrole extension

Revision ID: 0004_novedades_modulos
Revises: 0003_professionals_external_sync
Create Date: 2026-07-28
"""

from alembic import op
import sqlalchemy as sa

revision = "0004_novedades_modulos"
down_revision = "0003_professionals_external_sync"
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
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'jefe_medico'")
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'rrhh'")

    op.create_table(
        "novedades_servicio",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(length=120), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        *_audit_columns(),
    )
    op.create_index(
        "uq_novedades_servicio_nombre_active",
        "novedades_servicio",
        ["nombre"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "novedades_modulo",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("descripcion", sa.String(length=200), nullable=False),
        sa.Column("comentario", sa.String(length=500), nullable=True),
        sa.Column("valor", sa.Numeric(12, 2), nullable=False),
        *_audit_columns(),
    )

    op.create_table(
        "novedades_periodo",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(length=120), nullable=True),
        sa.Column("fecha_inicio", sa.Date(), nullable=False),
        sa.Column("fecha_fin", sa.Date(), nullable=False),
        sa.Column("estado", sa.String(length=20), nullable=False, server_default="open"),
        *_audit_columns(),
    )
    op.create_check_constraint(
        "ck_novedades_periodo_rango",
        "novedades_periodo",
        "fecha_inicio <= fecha_fin",
    )
    op.create_check_constraint(
        "ck_novedades_periodo_estado",
        "novedades_periodo",
        "estado IN ('open', 'closed')",
    )
    op.execute(
        """
        CREATE UNIQUE INDEX uq_novedades_periodo_one_open
        ON novedades_periodo ((estado))
        WHERE estado = 'open' AND deleted_at IS NULL
        """
    )

    op.create_table(
        "novedades_jefe_servicio",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("servicio_id", sa.Integer(), sa.ForeignKey("novedades_servicio.id"), nullable=False),
        *_audit_columns(),
    )
    op.create_index(
        "uq_novedades_jefe_servicio_active",
        "novedades_jefe_servicio",
        ["user_id", "servicio_id"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "novedades_profesional_servicio",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("professional_id", sa.Integer(), sa.ForeignKey("professionals.id"), nullable=False),
        sa.Column("servicio_id", sa.Integer(), sa.ForeignKey("novedades_servicio.id"), nullable=False),
        *_audit_columns(),
    )
    op.create_index(
        "uq_novedades_profesional_servicio_active",
        "novedades_profesional_servicio",
        ["professional_id", "servicio_id"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "novedades_asignacion_modulo",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("periodo_id", sa.Integer(), sa.ForeignKey("novedades_periodo.id"), nullable=False),
        sa.Column("servicio_id", sa.Integer(), sa.ForeignKey("novedades_servicio.id"), nullable=False),
        sa.Column("professional_id", sa.Integer(), sa.ForeignKey("professionals.id"), nullable=False),
        sa.Column("modulo_id", sa.Integer(), sa.ForeignKey("novedades_modulo.id"), nullable=False),
        *_audit_columns(),
    )

    op.create_table(
        "novedades_novedad",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("periodo_id", sa.Integer(), sa.ForeignKey("novedades_periodo.id"), nullable=False),
        sa.Column("servicio_id", sa.Integer(), sa.ForeignKey("novedades_servicio.id"), nullable=False),
        sa.Column("professional_id", sa.Integer(), sa.ForeignKey("professionals.id"), nullable=False),
        sa.Column("modulo_id", sa.Integer(), sa.ForeignKey("novedades_modulo.id"), nullable=False),
        sa.Column("valor", sa.Numeric(12, 2), nullable=False),
        sa.Column("justificacion", sa.String(length=1000), nullable=False),
        *_audit_columns(),
    )


def downgrade() -> None:
    op.drop_table("novedades_novedad")
    op.drop_table("novedades_asignacion_modulo")
    op.drop_table("novedades_profesional_servicio")
    op.drop_table("novedades_jefe_servicio")
    op.execute("DROP INDEX IF EXISTS uq_novedades_periodo_one_open")
    op.drop_table("novedades_periodo")
    op.drop_table("novedades_modulo")
    op.drop_table("novedades_servicio")
    # PG cannot easily remove enum values; leave userrole values in place on downgrade.
