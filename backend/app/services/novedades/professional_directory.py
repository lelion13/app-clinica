from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.novedades import NovedadesProfesionalServicio
from app.models.professional import Professional
from app.schemas.novedades import ProfesionalDirectoryItem


def list_professionals_for_servicio(db: Session, servicio_id: int | None = None) -> list[ProfesionalDirectoryItem]:
    """Adapter sobre `professionals`. Con servicio_id: solo asociados por ABM."""
    if servicio_id is not None:
        linked_ids = list(
            db.execute(
                select(NovedadesProfesionalServicio.professional_id).where(
                    NovedadesProfesionalServicio.servicio_id == servicio_id,
                    NovedadesProfesionalServicio.deleted_at.is_(None),
                )
            )
            .scalars()
            .all()
        )
        if not linked_ids:
            return []
        rows = list(
            db.execute(
                select(Professional)
                .where(
                    Professional.deleted_at.is_(None),
                    Professional.id.in_(linked_ids),
                    Professional.is_active.is_(True),
                )
                .order_by(Professional.full_name)
            )
            .scalars()
            .all()
        )
        return [_to_item(row) for row in rows]

    rows = list(
        db.execute(
            select(Professional)
            .where(Professional.deleted_at.is_(None), Professional.is_active.is_(True))
            .order_by(Professional.full_name)
        )
        .scalars()
        .all()
    )
    return [_to_item(row) for row in rows]


def _to_item(row: Professional) -> ProfesionalDirectoryItem:
    return ProfesionalDirectoryItem(
        id=row.id,
        full_name=row.full_name,
        license_number=row.license_number,
        specialty=row.specialty,
        is_active=row.is_active,
    )
