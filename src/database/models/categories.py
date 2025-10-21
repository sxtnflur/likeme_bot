from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from .generated_images import GeneratedImage


class Category(Base):
    __tablename__ = 'categories'

    key: Mapped[str] = mapped_column(primary_key=True)


class GeneratedImageCategory(Base):
    __tablename__ = 'generated_images_categories'

    category_key: Mapped[str] = mapped_column(ForeignKey(Category.key), primary_key=True)
    image_id: Mapped[int] = mapped_column(ForeignKey(GeneratedImage.id), primary_key=True)

    image = relationship(GeneratedImage, foreign_keys=[image_id])