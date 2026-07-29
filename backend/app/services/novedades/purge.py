from fastapi import HTTPException, status
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.novedades import NovedadesAsignacionModulo, NovedadesNovedad, NovedadesProfesionalServicio
from app.models.user import User, UserRole
from app.schemas.novedades import NovedadesTransaccionalPurgeResponse


def purge_novedades_transaccional(db: Session, user: User) -> NovedadesTransaccionalPurgeResponse:
    if user.role not in (UserRole.admin, UserRole.rrhh):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes")

    deleted_asignaciones = db.execute(delete(NovedadesAsignacionModulo)).rowcount or 0
    deleted_novedades = db.execute(delete(NovedadesNovedad)).rowcount or 0
    deleted_links = db.execute(delete(NovedadesProfesionalServicio)).rowcount or 0
    db.commit()
    return NovedadesTransaccionalPurgeResponse(
        deleted_asignaciones=deleted_asignaciones,
        deleted_novedades=deleted_novedades,
        deleted_profesional_servicios=deleted_links,
    )
