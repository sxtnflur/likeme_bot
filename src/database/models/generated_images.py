from database.models.base import Base, IntPk, TgId, CreatedAt
from sqlalchemy import TEXT, ARRAY, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class GeneratedImage(Base):
    __tablename__ = 'generated_images'

    id: Mapped[IntPk]
    user_id: Mapped[TgId] = mapped_column(ForeignKey('users.id'))
    image_url: Mapped[str]
    prompt: Mapped[str] = mapped_column(TEXT)
    prompt_images: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    is_private: Mapped[bool] = mapped_column(server_default='False')
    created_at: Mapped[CreatedAt]

    user = relationship('User', foreign_keys=[user_id])
    categories = relationship('Category', secondary='generated_images_categories', uselist=True)
    categories_secondary = relationship('GeneratedImageCategory', back_populates='image')


class Like(Base):
    __tablename__ = 'likes'

    user_id: Mapped[TgId] = mapped_column(ForeignKey('users.id'), primary_key=True)
    image_id: Mapped[int] = mapped_column(ForeignKey(GeneratedImage.id), primary_key=True)

    user = relationship('User', foreign_keys=[user_id])
    image = relationship(GeneratedImage, foreign_keys=[image_id])