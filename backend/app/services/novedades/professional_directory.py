from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.novedades import NovedadesProfesionalServicio
from app.models.professional import Professional
from app.schemas.novedades import ProfesionalDirectoryItem


def list_professionals_for_servicio(
    db: Session,
    servicio_id: int | None = None,
    *,
    q: str | None = None,
    exclude_linked: bool = False,
) -> list[ProfesionalDirectoryItem]:
    """Adapter sobre `professionals`.

    - Con servicio_id y exclude_linked=False: solo asociados al servicio (Carga).
    - Con servicio_id y exclude_linked=True: activos no asociados (Mis profesionales picker).
    - Sin servicio_id: todos los activos.
    """
    query = select(Professional).where(Professional.deleted_at.is_(None), Professional.is_active.is_(True))

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
        if exclude_linked:
            if linked_ids:
                query = query.where(Professional.id.notin_(linked_ids))
        else:
            if not linked_ids:
                return []
            query = query.where(Professional.id.in_(linked_ids))

    if q and q.strip():
        needle = f"%{q.strip()}%"
        query = query.where(
            or_(
                Professional.full_name.ilike(needle),
                Professional.license_number.ilike(needle),
                Professional.external_document.ilike(needle),
            )
        )

    rows = list(db.execute(query.order_by(Professional.full_name)).scalars().all())
    return [_to_item(row) for row in rows]


def _to_item(row: Professional) -> ProfesionalDirectoryItem:
    return ProfesionalDirectoryItem(
        id=row.id,
        full_name=row.full_name,
        license_number=row.license_number,
        external_document=row.external_document,
        specialty=row.specialty,
        is_active=row.is_active,
    )
