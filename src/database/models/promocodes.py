from database.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column


class Promocode(Base):
    __tablename__ = 'promocodes'

    code: Mapped[str] = mapped_column(primary_key=True)
    sale_percentage: Mapped[int]
    type: Mapped[str] = mapped_column(server_default='all')