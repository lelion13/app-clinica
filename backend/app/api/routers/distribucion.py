from fastapi import APIRouter, Depends

from app.api.deps import require_operator_or_admin
from app.models.user import User
from app.schemas.distribucion import HorariosActivosResponse
from app.services.distribucion import horarios_activos as horarios_activos_service

router = APIRouter()


@router.get("/ocupacion/horarios-activos", response_model=HorariosActivosResponse)
def ocupacion_horarios_activos(user: User = Depends(require_operator_or_admin)) -> HorariosActivosResponse:
    _ = user
    return horarios_activos_service.fetch_horarios_activos()
