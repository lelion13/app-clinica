"""Tabla snapshot horarios activos (Distribución → Ocupación)

Revision ID: 0011_ocupacion_horario
Revises: 0010_bonos_resumen
Create Date: 2026-08-03
"""

from alembic import op
import sqlalchemy as sa

revision = "0011_ocupacion_horario"
down_revision = "0010_bonos_resumen"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ocupacion_horario_activo",
        sa.Column("id_dato", sa.String(length=80), primary_key=True),
        sa.Column("horario_id", sa.Integer(), nullable=True),
        sa.Column("id_agenda", sa.Integer(), nullable=True),
        sa.Column("id_dominio", sa.Integer(), nullable=True),
        sa.Column("area_jerarquica_id", sa.Integer(), nullable=True),
        sa.Column("nombre_agenda", sa.String(length=500), nullable=True),
        sa.Column("tipo", sa.String(length=120), nullable=True),
        sa.Column("especialidad_agenda", sa.String(length=200), nullable=True),
        sa.Column("medico", sa.String(length=200), nullable=True),
        sa.Column("especialidad", sa.String(length=200), nullable=True),
        sa.Column("tipo_agenda", sa.String(length=80), nullable=True),
        sa.Column("consultorio", sa.String(length=120), nullable=True),
        sa.Column("dia", sa.String(length=40), nullable=True),
        sa.Column("dia_de_agenda", sa.String(length=40), nullable=True),
        sa.Column("fecha_desde", sa.String(length=40), nullable=True),
        sa.Column("hora_desde", sa.String(length=40), nullable=True),
        sa.Column("fecha_hasta", sa.String(length=40), nullable=True),
        sa.Column("hora_hasta", sa.String(length=40), nullable=True),
        sa.Column("periodo_desde", sa.String(length=40), nullable=True),
        sa.Column("periodo_hasta", sa.String(length=40), nullable=True),
        sa.Column("duracion_turno", sa.Float(), nullable=True),
        sa.Column("cantidad_turnos", sa.Float(), nullable=True),
        sa.Column("cantidad_sobreturno", sa.Float(), nullable=True),
        sa.Column("horas_funcionamiento", sa.Float(), nullable=True),
        sa.Column("capacidad_turnos_15_min", sa.Float(), nullable=True),
        sa.Column("tiempo_consultorio", sa.Float(), nullable=True),
        sa.Column("estado_agenda", sa.String(length=20), nullable=True),
        sa.Column("estado_horario", sa.String(length=20), nullable=True),
        sa.Column("atiende_feriado", sa.String(length=8), nullable=True),
        sa.Column("dias_limite_visualizacion_pantalla", sa.Integer(), nullable=True),
        sa.Column("dias_solicitud_turnos", sa.Integer(), nullable=True),
        sa.Column("medico_responsable", sa.String(length=200), nullable=True),
        sa.Column("medico_responsable_equipo", sa.String(length=200), nullable=True),
        sa.Column("fecha_ultima_modificacion_agenda", sa.String(length=40), nullable=True),
        sa.Column("fecha_creacion_horario", sa.String(length=40), nullable=True),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_ocupacion_horario_activo_horario_id", "ocupacion_horario_activo", ["horario_id"])
    op.create_index("ix_ocupacion_horario_activo_id_agenda", "ocupacion_horario_activo", ["id_agenda"])
    op.create_index("ix_ocupacion_horario_activo_id_dominio", "ocupacion_horario_activo", ["id_dominio"])
    op.create_index("ix_ocupacion_horario_activo_dia", "ocupacion_horario_activo", ["dia"])
    op.create_index("ix_ocupacion_horario_activo_fecha_hasta", "ocupacion_horario_activo", ["fecha_hasta"])


def downgrade() -> None:
    op.drop_index("ix_ocupacion_horario_activo_fecha_hasta", table_name="ocupacion_horario_activo")
    op.drop_index("ix_ocupacion_horario_activo_dia", table_name="ocupacion_horario_activo")
    op.drop_index("ix_ocupacion_horario_activo_id_dominio", table_name="ocupacion_horario_activo")
    op.drop_index("ix_ocupacion_horario_activo_id_agenda", table_name="ocupacion_horario_activo")
    op.drop_index("ix_ocupacion_horario_activo_horario_id", table_name="ocupacion_horario_activo")
    op.drop_table("ocupacion_horario_activo")
