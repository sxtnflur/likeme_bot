import aiogram
from bot import keyboards
from database import AvatarsRepo, UsersRepo, ModelsRepo, FalRequestsRepo
from services.storage import BaseStorage
from sqlalchemy.ext.asyncio import AsyncSession
from .ai.fal import upload_zip_by_file_ids, train_lora
from texts import get_texts


class AvatarsService:
    def __init__(self, bot: aiogram.Bot, storage: BaseStorage):
        self.bot = bot
        self.file_storage = storage

    async def add_simple_avatar(self, user_id: int, file_id: str, name: str, db: AsyncSession) -> None:
        file = await self.bot.download(file_id)
        async with self.file_storage.start_transaction() as storage:
            image_url = await storage.save_file_get_url(
                file.read(),
                filename=name + '.jpg',
                folder=f'/avatars/simple/{user_id}'
            )
            avatar_id = await AvatarsRepo(db).add_and_get(
                obj=dict(
                    user_id=user_id,
                    name=name
                ),
                get_field='id'
            )
            await ModelsRepo(db).add(
                avatar_id=avatar_id,
                photos=[image_url],
                level=0
            )
            await UsersRepo(db).update(
                filters=dict(id=user_id),
                updates=dict(current_avatar_id=avatar_id,
                             can_create_avatar=True)
            )

    async def create_modeling_model(
            self, user_id: int, file_ids: list[str],
            model_id: int,
            db: AsyncSession
    ) -> None:
        zip_url = await upload_zip_by_file_ids(
            user_id=user_id, bot=self.bot,
            file_ids=file_ids
        )
        print(f'{zip_url=}')
        req_id = await train_lora(zip_url)
        print(f'{req_id=}')
        await FalRequestsRepo(db).add(
            id=req_id,
            data=dict(model_id=model_id)
        )
        await ModelsRepo(db).update(
            filters=dict(id=model_id),
            updates=dict(status='training')
        )

    async def add_modeling_model_to_avatar(
            self,
            diffusers_url: str,
            model_id: int,
            db: AsyncSession
    ) -> None:
        await ModelsRepo(db).update(
            filters=dict(id=model_id),
            updates=dict(diffusers_url=diffusers_url, status='ready')
        )
        avatar_id = await ModelsRepo(db).get_one_field('avatar_id', id=model_id)
        user_id = await AvatarsRepo(db).get_one_field('user_id', id=avatar_id)
        language = await UsersRepo(db).get_one_field('language', id=user_id)
        texts = get_texts(language)
        await self.bot.send_message(
            chat_id=user_id,
            text='Модель успешно обучена. Теперь вы можете создавать фото Portrait',
            reply_markup=keyboards.to_create_image(texts)
        )