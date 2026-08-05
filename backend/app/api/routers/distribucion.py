from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_operator_or_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.consulting_room import AgendaLookupResponse
from app.schemas.distribucion import (
    AgendaFilterOptionsResponse,
    AgendaOcupacionEventsResponse,
    HorariosActivosResponse,
    HorariosActivosSyncResponse,
)
from app.services import room_agenda_map as room_agenda_map_service
from app.services.distribucion import agenda_ocupacion as agenda_ocupacion_service
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


@router.get("/ocupacion/agenda/filter-options", response_model=AgendaFilterOptionsResponse)
def ocupacion_agenda_filter_options(
    db: Session = Depends(get_db),
    user: User = Depends(require_operator_or_admin),
) -> AgendaFilterOptionsResponse:
    _ = user
    return agenda_ocupacion_service.list_filter_options(db)


@router.get("/ocupacion/agenda-lookup", response_model=AgendaLookupResponse)
def ocupacion_agenda_lookup(
    q: str = Query(default="", min_length=0),
    db: Session = Depends(get_db),
    user: User = Depends(require_operator_or_admin),
) -> AgendaLookupResponse:
    _ = user
    return room_agenda_map_service.lookup_agendas_by_medico(db, q)


@router.get("/ocupacion/agenda/events", response_model=AgendaOcupacionEventsResponse)
def ocupacion_agenda_events(
    start: str = Query(...),
    end: str = Query(...),
    location_id: int | None = Query(default=None),
    id_dominio: list[str] | None = Query(default=None),
    tipo: list[str] | None = Query(default=None),
    especialidad: list[str] | None = Query(default=None),
    medico: list[str] | None = Query(default=None),
    dia: list[str] | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(require_operator_or_admin),
) -> AgendaOcupacionEventsResponse:
    _ = user
    return agenda_ocupacion_service.list_agenda_events(
        db,
        start=start,
        end=end,
        location_id=location_id,
        id_dominio=id_dominio,
        tipo=tipo,
        especialidad=especialidad,
        medico=medico,
        dia=dia,
    )
