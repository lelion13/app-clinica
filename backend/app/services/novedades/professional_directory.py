from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.novedades import NovedadesProfesional, NovedadesProfesionalServicio
from app.schemas.novedades import ProfesionalDirectoryItem


def list_professionals_for_servicio(
    db: Session,
    servicio_id: int | None = None,
    *,
    q: str | None = None,
    exclude_linked: bool = False,
) -> list[ProfesionalDirectoryItem]:
    """Directory sobre catálogo Novedades (`novedades_profesional`).

    - Con servicio_id y exclude_linked=False: asociados activos al servicio (Carga).
    - Con servicio_id y exclude_linked=True: activos no asociados (picker Mis profesionales).
    - Sin servicio_id: todos los activos.
    """
    query = select(NovedadesProfesional).where(
        NovedadesProfesional.deleted_at.is_(None),
        NovedadesProfesional.is_active.is_(True),
    )

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
                query = query.where(NovedadesProfesional.id.notin_(linked_ids))
        else:
            if not linked_ids:
                return []
            query = query.where(NovedadesProfesional.id.in_(linked_ids))

    if q and q.strip():
        needle = f"%{q.strip()}%"
        query = query.where(
            or_(
                NovedadesProfesional.full_name.ilike(needle),
                NovedadesProfesional.codprof.ilike(needle),
            )
        )

    rows = list(db.execute(query.order_by(NovedadesProfesional.full_name)).scalars().all())
    return [_to_item(row) for row in rows]


def _to_item(row: NovedadesProfesional) -> ProfesionalDirectoryItem:
    return ProfesionalDirectoryItem(
        id=row.id,
        full_name=row.full_name,
        codprof=row.codprof,
        legajo=row.legajo,
        license_number=None,
        external_document=None,
        specialty=None,
        is_active=row.is_active,
    )
