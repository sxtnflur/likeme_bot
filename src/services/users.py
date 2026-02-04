import aiogram
from aiogram.types import PhotoSize
from bg_tasks import BgTasksFactory
from config import settings
from database import UsersRepo
from services.storage import BaseStorage
from sqlalchemy.ext.asyncio import AsyncSession


class UsersService:
    def __init__(self, bot: aiogram.Bot, storage: BaseStorage,
                 bg_tasks_factory: BgTasksFactory):
        self.storage = storage
        self.bot = bot
        self.bg_tasks_factory = bg_tasks_factory

    async def __add_user_to_db(
        self, tg_id: int, username: str | None,
        first_name: str, last_name: str | None,
        language: str,
        avatar_url: str | None,
        db: AsyncSession
    ):
        if language not in settings.ENABLE_LANGUAGES:
            language = settings.DEFAULT_LANGUAGE

        not_update = ['id', 'language', 'image_generations']

        user_exists = await UsersRepo(db).exists(id=tg_id)

        await UsersRepo(db).add_or_update(
            values=dict(id=tg_id, username=username,
                        first_name=first_name, last_name=last_name,
                        language=language,
                        avatar_url=avatar_url,
                        image_generations=3
                        ),
            on_conflict=['id'],
            not_update=not_update
        )

        if user_exists:
            await self.bg_tasks_factory.notifications.on_first_start_bot(
                user_id=tg_id, language=language
            )

    async def add_user_with_avatar(
        self,
        avatar: bytes,
        tg_id: int, username: str | None,
        first_name: str, last_name: str | None,
        language: str,
        *,
        db: AsyncSession
    ):
        async with self.storage.start_transaction() as cdn:
            avatar_url = await cdn.save_file_get_url(
                file=avatar,
                filename=f'{tg_id}.jpg',
                folder=f'/avatars',
                replace_by_file_path=True
            )
            print(f'{avatar_url=}')
            await self.__add_user_to_db(
                tg_id, username, first_name, last_name,
                language=language,
                avatar_url=avatar_url, db=db
            )

    async def add_user(self,
                       tg_id: int, username: str | None,
                       first_name: str, last_name: str | None,
                       language: str,
                       *,
                       db: AsyncSession
                       ) -> None:
        profile_photos = await self.bot.get_user_profile_photos(
            user_id=tg_id, limit=1
        )
        if profile_photos.total_count:
            avatar_file_id = profile_photos.photos[0][-1].file_id
            avatar_file = await self.bot.download(avatar_file_id)
            await self.add_user_with_avatar(
                avatar_file.read(),
                tg_id, username,
                first_name, last_name,
                language=language,
                db=db
            )
        else:
            await self.__add_user_to_db(
                tg_id, username,
                first_name, last_name,
                language=language,
                avatar_url=None, db=db
            )

    async def add_user_from_aiogram(self, user: aiogram.types.User, language: str, db: AsyncSession) -> None:

        await self.add_user(
            tg_id=user.id, username=user.username,
            first_name=user.first_name, last_name=user.last_name,
            language=language,
            db=db
        )