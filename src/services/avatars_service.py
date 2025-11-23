import base64
import io

import aiogram
from bot import keyboards
from database import AvatarsRepo, UsersRepo, FalRequestsRepo
from services.storage import BaseStorage
from sqlalchemy.ext.asyncio import AsyncSession
from .ai import prompts
from .ai.fal import train_lora
from texts import get_texts
from .ai.fal.utils import upload_zip_by_io
from .ai.openai_service import OpenAIService


class AvatarsService:
    def __init__(self, bot: aiogram.Bot, storage: BaseStorage,
                 openai: OpenAIService):
        self.bot = bot
        self.file_storage = storage
        self.openai = openai

    async def check_if_user_can_train_avatar(self, user_id: int, db: AsyncSession) -> bool:
        return await AvatarsRepo(db).exists(
            user_id=user_id, status='added', level=0
        )

    async def create_avatar(self, user_id: int, level: int,
                            db: AsyncSession) -> int:
        return await AvatarsRepo(db).add_and_get(
            obj=dict(
                user_id=user_id,
                level=level,
                status='added'
            ),
            get_field='id'
        )

    async def train_simple_avatar(
            self, user_id: int,
            avatar_id: int, file_id: str,
            name: str,
            db: AsyncSession
    ) -> None:
        file = await self.bot.download(file_id)
        async with self.file_storage.start_transaction() as storage:
            image_url = await storage.save_file_get_url(
                file.read(),
                filename=str(user_id) + '.jpg',
                folder=f'/avatars/simple/'
            )
            # avatar_id = await AvatarsRepo(db).add_and_get(
            #     obj=dict(
            #         user_id=user_id,
            #         name=name
            #     ),
            #     get_field='id'
            # )
            await AvatarsRepo(db).update(
                filters=dict(
                      id=avatar_id
                ),
                updates=dict(
                    model_data=image_url,
                    level=0,
                    name=name,
                    status='ready'
                )
            )

            # await ModelsRepo(db).add(
            #     avatar_id=for_avatar_id,
            #     photos=[image_url],
            #     level=0
            # )
            await UsersRepo(db).update(
                filters=dict(id=user_id),
                updates=dict(current_avatar_id=avatar_id)
            )

    async def start_train_portrait_avatar(
            self,
            file_ids: list[str],
            avatar_id: int,
            db: AsyncSession
    ):
        zip_url = await self._prepare_images(file_ids)
        print(f'{zip_url=}')
        req_id = await train_lora(zip_url)
        print(f'{req_id=}')
        await FalRequestsRepo(db).add(
            id=req_id,
            data=dict(avatar_id=avatar_id)
        )
        await AvatarsRepo(db).update(
            filters=dict(id=avatar_id),
            updates=dict(
                status='training'
            )
        )

    async def on_trained_portrait_avatar(
            self,
            request_id: str,
            diffusers_url: str,
            db: AsyncSession
    ):
        fal_req = await FalRequestsRepo(db).get_one(
            id=request_id
        )
        avatar_id = fal_req.data.get('avatar_id')
        await AvatarsRepo(db).update(
            filters=dict(id=avatar_id),
            updates=dict(
                status='ready',
                model_data=diffusers_url
            )
        )
        language = await UsersRepo(db).get_one_field('language', id=fal_req.user_id)
        texts = get_texts(language)
        await self.bot.send_message(
            chat_id=fal_req.user_id,
            text='Модель успешно обучена. Теперь вы можете создавать фото Portrait',
            reply_markup=keyboards.to_create_image(texts)
        )

        await FalRequestsRepo(db).delete(id=request_id)

    async def _prepare_images(self, file_ids: list[str]) -> str:
        files = []
        for i, file_id in enumerate(file_ids):
            file = await self.bot.download(file_id)
            file.name = f'{i}.jpg'
            files.append(file)

            resp = await self.openai.send_images(
                photo_urls=[f'data:image/jpeg;base64,{base64.b64encode(file.read()).decode("utf-8")}'],
                caption=prompts.DESCRIBE_IMAGE_PROMPT,
                model='gpt-5-mini'
            )
            descr_file = io.BytesIO()
            descr_file.write(resp.text_answer.encode('utf-8'))
            descr_file.name = f'{i}.txt'
            descr_file.seek(0)
            files.append(descr_file)

        return await upload_zip_by_io(files)