from decimal import Decimal

from sqlalchemy.orm import Session

from app.schemas.novedades import ValorHoraUpdateRequest
from app.services.novedades.helpers import get_or_create_config


def get_valor_hora(db: Session) -> tuple[Decimal, object]:
    cfg = get_or_create_config(db)
    return Decimal(cfg.valor_hora), cfg.updated_at


def set_valor_hora(db: Session, payload: ValorHoraUpdateRequest, actor_id: int) -> tuple[Decimal, object]:
    from datetime import datetime

    cfg = get_or_create_config(db)
    cfg.valor_hora = Decimal(payload.valor_hora)
    cfg.updated_at = datetime.utcnow()
    cfg.updated_by = actor_id
    db.commit()
    db.refresh(cfg)
    return Decimal(cfg.valor_hora), cfg.updated_at
