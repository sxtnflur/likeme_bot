import datetime
import aiogram
import aiohttp
from aiogram.types import Message
from bot import keyboards
from bot.exceptions import SendToUserException
from config import settings
from enums.generation import AspectRatio
from services.categories import CategoriesService
from services.remixing import RemixingService
from services.translation import TranslationService
from sqlalchemy.ext.asyncio import AsyncSession
from database import UsersRepo, AvatarsRepo, GeneratedImagesRepo, GeneratedImagesCategoriesRepo
from services.ai.fal import nanobanana
from texts import Texts
from utils.convert import image_url_to_pil, image_file_id_to_pil
from utils.do_while import send_action_while_do_func
from services.storage.base import BaseStorage
from services.ai.fal import flux


class ImageGeneratorService:
    def __init__(self, bot: aiogram.Bot, file_storage: BaseStorage,
                 categories_service: CategoriesService,
                 translation_service: TranslationService,
                 remixing_service: RemixingService):
        self.bot = bot
        self.storage = file_storage
        self.categories_service = categories_service
        self.translation_service = translation_service
        self.remixing_service = remixing_service

    async def generate_image(self,
                             message: Message,
                             user_id: int,
                             prompt: str,
                             db: AsyncSession,
                             texts: Texts,
                             is_private: bool,
                             ratio: AspectRatio,
                             session: aiohttp.ClientSession,
                             prompt_image_file_ids: list[str] | None = None,
                             prompt_image_urls: list[str] | None = None,
                             model_level: int = 0
                             ) -> None:
        try:
            updated_generations = await UsersRepo(db).decrease_field(
                filters=dict(id=user_id),
                field='image_generations',
                value=1
            )
        except:
            raise SendToUserException(
                texts.generation.NO_GENERATIONS_MORE,
                reply_markup=keyboards.start_buy(texts)
            )

        avatar = await AvatarsRepo(db).get_by_user_current(user_id)
        if not avatar:
            raise SendToUserException(
                texts.generation.NO_AVATAR_ELSE
            )

        model = list(filter(lambda x: x.level == model_level, avatar.models))[0]
        if not prompt_image_urls:
            prompt_image_urls = []

        async with self.storage.start_transaction() as cdn:
            try:
                if model_level == 0:
                    if not model.photos:
                        raise Exception('Нет photos')

                    image_urls = model.photos
                    if prompt_image_file_ids and not prompt_image_urls:
                        for file_id in prompt_image_file_ids:
                            file_ = await self.bot.get_file(file_id)
                            file = await self.bot.download(file_id)
                            prompt_image_url = await cdn.save_file_get_url(
                                file.read(),
                                filename=file_.file_path.split('/')[-1],
                                folder=f'prompt_images/{user_id}',
                                replace_by_file_path=False
                            )
                            prompt_image_urls.append(prompt_image_url)
                    image_urls += prompt_image_urls

                    ratio_ = ratio.get_aspects()
                    coro = nanobanana.edit_image(
                        prompt,
                        image_urls=image_urls,
                        num_images=1,
                        aspect_ratio=f'{ratio_[0]}:{ratio_[1]}'
                    )
                elif model_level == 1:
                    if not model.diffusers_url:
                        raise SendToUserException(
                            'Ваша модель невалидна', add_support=True
                        )
                    prompt = await self.translation_service.translate_ru_to_en(prompt)

                    if prompt_image_file_ids or prompt_image_urls:
                        raise SendToUserException(
                            'Эта модель не работает с промпт-фотографиями'
                        )
                    else:
                        coro = flux.generate_images(
                            prompt,
                            lora=model.diffusers_url,
                            photo_format=ratio.get_wh()
                        )
                else:
                    raise SendToUserException(
                        texts.generation.UNPREDICTABLE_ERROR
                    )

                wait_msg = None
                if message.text:
                    wait_msg = await message.edit_text(
                        text=texts.generation.wait_message(prompt, is_private),
                        reply_markup=None
                    )
                elif message.caption:
                    wait_msg = await message.edit_caption(
                        text=texts.generation.wait_message(prompt, is_private),
                        reply_markup=None
                    )

                images = await send_action_while_do_func(
                    coroutine=coro,
                    chat_id=user_id,
                    bot=self.bot,
                    action='upload_photo'
                )
                res_image_url_ = images[0]

                if wait_msg:
                    await wait_msg.delete()

                await self.bot.send_photo(
                    chat_id=user_id,
                    photo=res_image_url_,
                    caption=texts.generation.on_image_generated(
                        prompt=prompt, is_private=is_private
                    )
                )
            except Exception as e:
                print(f'{e=}')
                raise SendToUserException(
                    text=texts.generation.ON_FAILED_GENERATION
                )

            file = await session.get(res_image_url_)
            res_image_url = await cdn.save_file_get_url(
                file=await file.read(),
                filename=f'{datetime.datetime.utcnow().timestamp().hex()}.jpg',
                folder=f'/generated_images/{user_id}'
            )

        image_id = await GeneratedImagesRepo(db).add_and_get(
            dict(
                user_id=user_id,
                model_id=model.id,
                image_url=res_image_url,
                prompt=prompt,
                prompt_images=prompt_image_urls,
                is_private=is_private,
                ratio=ratio.value
            ),
            get_field='id'
        )

        categories = await self.categories_service.generate_categories_for_image(
            image_url=res_image_url
        )
        await GeneratedImagesCategoriesRepo(db).add_all(
            list(map(lambda key: dict(category_key=key,
                                      image_id=image_id), categories))
        )

        await self.bot.send_message(
            chat_id=user_id,
            text=texts.generation.after_image_generated(
                is_private=is_private,
                webapp_post_url=settings.WEBAPP_DIRECT_URL + f'?startapp=post_{image_id}',
                remix_url=self.remixing_service.create_start_link(image_id)
            )
        )