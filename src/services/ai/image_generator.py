import datetime

import aiogram
import aiohttp
from PIL import Image
import io

from aiogram.types import Message
from services.storage import BaseStorage
from sqlalchemy.ext.asyncio import AsyncSession
from database import UsersRepo, AvatarsRepo, GeneratedImagesRepo
from services.ai.fal import nanobanana
from texts import Texts
from utils.convert import image_url_to_pil, image_file_id_to_pil
from utils.do_while import send_action_while_do_func
from services.storage.base import BaseStorage


class ImageGeneratorService:
    def __init__(self, bot: aiogram.Bot, file_storage: BaseStorage):
        self.bot = bot
        self.storage = file_storage

    async def generate_image(self,
                             message: Message,
                             user_id: int,
                             prompt: str,
                             db: AsyncSession, texts: Texts,
                             prompt_image_file_ids: list[str],
                             is_private: bool,
                             session: aiohttp.ClientSession
                             ):
        try:
            updated_generations = await UsersRepo(db).decrease_field(
                filters=dict(id=user_id),
                field='image_generations',
                value=1
            )
        except:
            await self.bot.send_message(
                chat_id=user_id,
                text=texts.generation.NO_GENERATIONS_MORE
            )
            return

        avatar = await AvatarsRepo(db).get_by_user_current(user_id)
        if not avatar:
            await self.bot.send_message(
                chat_id=user_id,
                text=texts.generation.NO_AVATAR_ELSE
            )
            return

        prompt_images = None
        if avatar.photos:
            images = [await image_url_to_pil(str(avatar.photos[0]), session=session)]
            if prompt_image_file_ids:
                prompt_images = [
                    await image_file_id_to_pil(file_id, bot=self.bot)
                    for file_id in prompt_image_file_ids
                ]
                images += prompt_images

            coro = nanobanana.edit_image(
                prompt,
                images=images,
                num_images=1
            )
        elif avatar.model:
            await self.bot.send_message(
                chat_id=user_id,
                text=texts.generation.UNPREDICTABLE_ERROR
            )
            return
        else:
            await self.bot.send_message(
                chat_id=user_id,
                text=texts.generation.UNPREDICTABLE_ERROR
            )
            return

        wait_msg = await message.edit_text(
            text=texts.generation.wait_message(prompt, is_private),
            reply_markup=None
        )
        images = await send_action_while_do_func(
            coroutine=coro,
            chat_id=user_id,
            bot=self.bot,
            action='upload_photo'
        )
        res_image_url = images[0]

        await wait_msg.delete()

        await self.bot.send_photo(
            chat_id=user_id,
            photo=res_image_url,
            caption=texts.generation.ON_IMAGE_GENERATED
        )

        async with self.storage.start_transaction() as cdn:
            file = await session.get(res_image_url)
            res_image_url = await cdn.save_file_get_url(
                file=await file.read(),
                filename=f'{datetime.datetime.utcnow().timestamp().hex()}.jpg',
                folder=f'/generated_images/{user_id}'
            )
            await GeneratedImagesRepo(db).add(
                user_id=user_id,
                image_url=res_image_url,
                prompt=prompt,
                prompt_images=prompt_images,
                is_private=is_private
            )