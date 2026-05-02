from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_operator_or_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.stats import StatsSummaryResponse
from app.services.stats_service import build_stats_summary

router = APIRouter()


@router.get("/summary", response_model=StatsSummaryResponse)
def stats_summary(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    _: User = Depends(require_operator_or_admin),
    location_ids: list[int] | None = Query(default=None, description="Filtrar por ubicación(es)"),
    room_ids: list[int] | None = Query(default=None, description="Filtrar por consultorio(s)"),
    professional_ids: list[int] | None = Query(default=None, description="Filtrar reservas por profesional(es)"),
) -> StatsSummaryResponse:
    try:
        return build_stats_summary(
            db,
            start_date,
            end_date,
            location_ids or [],
            room_ids or [],
            professional_ids or [],
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
