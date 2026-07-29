"""fecha_realizacion en asignaciones y novedades

Revision ID: 0007_fecha_realizacion
Revises: 0006_mod_svc_valor_hora
Create Date: 2026-07-29
"""

from alembic import op
import sqlalchemy as sa

revision = "0007_fecha_realizacion"
down_revision = "0006_mod_svc_valor_hora"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("novedades_asignacion_modulo", sa.Column("fecha_realizacion", sa.Date(), nullable=True))
    op.add_column("novedades_novedad", sa.Column("fecha_realizacion", sa.Date(), nullable=True))

    op.execute(
        """
        UPDATE novedades_asignacion_modulo a
        SET fecha_realizacion = LEAST(
            GREATEST(CAST(a.created_at AS date), p.fecha_inicio),
            p.fecha_fin
        )
        FROM novedades_periodo p
        WHERE a.periodo_id = p.id
          AND a.fecha_realizacion IS NULL
        """
    )
    op.execute(
        """
        UPDATE novedades_novedad n
        SET fecha_realizacion = LEAST(
            GREATEST(CAST(n.created_at AS date), p.fecha_inicio),
            p.fecha_fin
        )
        FROM novedades_periodo p
        WHERE n.periodo_id = p.id
          AND n.fecha_realizacion IS NULL
        """
    )
    op.execute(
        """
        UPDATE novedades_asignacion_modulo
        SET fecha_realizacion = CAST(created_at AS date)
        WHERE fecha_realizacion IS NULL
        """
    )
    op.execute(
        """
        UPDATE novedades_novedad
        SET fecha_realizacion = CAST(created_at AS date)
        WHERE fecha_realizacion IS NULL
        """
    )

    op.alter_column("novedades_asignacion_modulo", "fecha_realizacion", nullable=False)
    op.alter_column("novedades_novedad", "fecha_realizacion", nullable=False)


def downgrade() -> None:
    op.drop_column("novedades_novedad", "fecha_realizacion")
    op.drop_column("novedades_asignacion_modulo", "fecha_realizacion")
