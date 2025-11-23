from sqlalchemy import JSON, BIGINT, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class FalRequest(Base):
    __tablename__ = 'fal_requests'

    id: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('users.id'))
    data: Mapped[dict] = mapped_column(JSON)