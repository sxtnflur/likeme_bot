from database.models.base import Base, IntPk, TgId
# from enums.avatars import ModelStatus
from sqlalchemy import ARRAY, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Avatar(Base):
    __tablename__ = 'avatars'

    id: Mapped[IntPk]
    user_id: Mapped[TgId] = mapped_column(ForeignKey('users.id'))
    name: Mapped[str | None]

    model_data: Mapped[str | None]
    level: Mapped[int] = mapped_column(server_default='0')
    #  0 - Simple (Nanobanana),  1 - Portrait (Flux portrait)

    status: Mapped[str] = mapped_column(server_default='ready')

    # model: Mapped[str | None]
    # level: Mapped[int] = mapped_column(server_default='0')
    # 0 - Simple (Nanobanana


# class Model(Base):
#     __tablename__ = 'models'
#
#     id: Mapped[IntPk]
#     avatar_id: Mapped[int] = mapped_column(ForeignKey(Avatar.id))
#     photos: Mapped[list[str] | None] = mapped_column(ARRAY(String))
#     diffusers_url: Mapped[str | None]
#     level: Mapped[int] = mapped_column(server_default='0')
#     #  0 - Simple (Nanobanana,  1 - Portrait (Flux portrait)
#
#     status: Mapped[str] = mapped_column(server_default='ready')
#
#     avatar = relationship(Avatar, foreign_keys=[avatar_id])
