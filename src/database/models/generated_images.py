from database.models.base import Base, IntPk, TgIdFk, CreatedAt
from sqlalchemy import TEXT, ARRAY, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class GeneratedImage(Base):
    __tablename__ = 'generated_images'

    id: Mapped[IntPk]
    user_id: Mapped[TgIdFk] = mapped_column(ForeignKey('users.id'))
    image_url: Mapped[str]
    prompt: Mapped[str] = mapped_column(TEXT)
    prompt_images: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    created_at: Mapped[CreatedAt]

    user = relationship('User', foreign_keys=[user_id])