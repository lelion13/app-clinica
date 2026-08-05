from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.common import AuditMixin


class Location(AuditMixin, Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    # Código del endpoint de ocupación (id_dominio). Unique entre activas (índice parcial en migración).
    id_dominio: Mapped[int] = mapped_column(Integer, nullable=False)
