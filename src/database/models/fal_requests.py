from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class FalRequest(Base):
    __tablename__ = 'fal_requests'

    id: Mapped[str] = mapped_column(primary_key=True)
    data: Mapped[dict] = mapped_column(JSON)