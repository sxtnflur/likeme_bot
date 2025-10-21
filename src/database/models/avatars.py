from database.models.base import Base, IntPk, TgId
from sqlalchemy import ARRAY, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class Avatar(Base):
    __tablename__ = 'avatars'

    id: Mapped[IntPk]
    user_id: Mapped[TgId] = mapped_column(ForeignKey('users.id'))
    name: Mapped[str]
    photos: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    model: Mapped[str | None]
    level: Mapped[int] = mapped_column(server_default='0')
    # 0 - Simple (Nanobanana)