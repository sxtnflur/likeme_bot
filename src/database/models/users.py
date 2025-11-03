from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TgIdPk, CreatedAt


class User(Base):
    __tablename__ = 'users'

    id: Mapped[TgIdPk]
    username: Mapped[str | None]
    first_name: Mapped[str]
    last_name: Mapped[str | None]
    language: Mapped[str | None]
    avatar_url: Mapped[str | None]
    image_generations: Mapped[int] = mapped_column(server_default='0')
    created_at: Mapped[CreatedAt]
    current_avatar_id: Mapped[int | None] = mapped_column(ForeignKey('avatars.id'))
    can_create_avatar: Mapped[bool] = mapped_column(server_default='True')

    current_avatar = relationship('Avatar', foreign_keys=[current_avatar_id])