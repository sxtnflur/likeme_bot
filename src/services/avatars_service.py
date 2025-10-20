import aiogram
from database import AvatarsRepo, UsersRepo
from services.storage import BaseStorage
from sqlalchemy.ext.asyncio import AsyncSession


class AvatarsService:
    def __init__(self, bot: aiogram.Bot, storage: BaseStorage):
        self.bot = bot
        self.file_storage = storage

    async def add_simple_avatar(self, user_id: int, file_id: str, name: str, db: AsyncSession) -> None:
        file = await self.bot.download(file_id)
        async with self.file_storage.start_transaction() as trans_cdn:
            image_url = await trans_cdn.save_file_get_url(file.read(),
                                                          filename=name + '.jpg',
                                                          folder=f'/avatars/simple/{user_id}'
                                                          )
            avatar_id = await AvatarsRepo(db).add_and_get(
                obj=dict(
                    user_id=user_id,
                    name=name,
                    photos=[image_url]
                ),
                get_field='id'
            )
            await UsersRepo(db).update(
                filters=dict(id=user_id),
                updates=dict(current_avatar_id=avatar_id)
            )
