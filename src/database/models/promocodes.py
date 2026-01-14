from database.models.base import Base
from sqlalchemy import ForeignKey, BIGINT
from sqlalchemy.orm import Mapped, mapped_column


class Promocode(Base):
    __tablename__ = 'promocodes'

    code: Mapped[str] = mapped_column(primary_key=True)
    sale_percentage: Mapped[int]
    type: Mapped[int] = mapped_column(server_default='0')


class UsedPromocodes(Base):
    __tablename__ = 'used_promocodes'

    promocode_code: Mapped[str] = mapped_column(ForeignKey(Promocode.code), primary_key=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('users.id'), primary_key=True)