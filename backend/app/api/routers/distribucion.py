from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_operator_or_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.distribucion import HorariosActivosResponse, HorariosActivosSyncResponse
from app.services.distribucion import horarios_activos as horarios_activos_service

router = APIRouter()


@router.get("/ocupacion/horarios-activos", response_model=HorariosActivosResponse)
def ocupacion_horarios_activos(
    db: Session = Depends(get_db),
    user: User = Depends(require_operator_or_admin),
) -> HorariosActivosResponse:
    _ = user
    return horarios_activos_service.list_horarios_activos(db)


@router.post("/ocupacion/horarios-activos/sync", response_model=HorariosActivosSyncResponse)
def ocupacion_horarios_activos_sync(
    db: Session = Depends(get_db),
    user: User = Depends(require_operator_or_admin),
) -> HorariosActivosSyncResponse:
    _ = user
    return horarios_activos_service.sync_horarios_activos(db)
