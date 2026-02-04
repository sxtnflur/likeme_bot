from database.models.base import Base, IntPk, TgId, UUIDPK, CreatedAt
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[UUIDPK]
    user_id: Mapped[TgId] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[CreatedAt]


class Payment(Base):
    __tablename__ = 'payments'

    id: Mapped[IntPk]
    user_id: Mapped[TgId] = mapped_column(ForeignKey('users.id'))
    amount: Mapped[float]
    package_id: Mapped[int | None]
    type: Mapped[str] = mapped_column(server_default='package')
    created_at: Mapped[CreatedAt]