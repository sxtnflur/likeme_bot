from typing import cast

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BufferedInputFile
from aiogram.utils.deep_linking import create_start_link, decode_payload, create_deep_link
from bot import keyboards
from database import GeneratedImagesRepo, AvatarsRepo, ModelsRepo
from enums.generation import AspectRatio
from schemas.avatars import AvatarSchema, AvatarWithModelsSchema
from sqlalchemy.ext.asyncio import AsyncSession
from texts import Texts
from config import settings


class RemixingService:
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    def create_start_link(self, generated_image_id: int) -> str:
        payload = f'remix-{generated_image_id}'
        return create_deep_link(
            username=cast(str, settings.BOT_USERNAME),
            link_type="start",
            payload=payload,
            encode=True,
            encoder=None
    )

    async def process_start_link(
        self,
        payload: str,
        user_id: int,
        texts: Texts,
        state: FSMContext,
        db: AsyncSession
    ) -> bool:
        """
        :param db:
        :param state:
        :param texts:
        :param payload: command.args
        :return: True - ссылка обработана, False = нет
        """
        payload = decode_payload(payload)
        if payload.startswith('remix-'):
            try:
                image_id = int(payload.split('remix-')[1])
            except Exception:
                return False

            await self.remix_gen_image(
                user_id=user_id,
                texts=texts,
                generated_image_id=image_id,
                state=state,
                db=db
            )
            return True
        return False

    async def remix_gen_image(self,
                              user_id: int,
                              texts: Texts,
                              generated_image_id: int,
                              state: FSMContext, db: AsyncSession):
        image = await GeneratedImagesRepo(db).get_one(user_id=user_id, id=generated_image_id)

        await state.update_data(
            create_image_prompt=image.prompt,
            create_image_prompt_image_urls=image.prompt_images
        )

        chosen_avatar: AvatarWithModelsSchema = await state.get_value('create_image_chosen_avatar')
        if not chosen_avatar:
            chosen_avatar = await AvatarsRepo(db).get_by_user_current(user_id=user_id)
            chosen_avatar = AvatarSchema.model_validate(chosen_avatar)
            await state.update_data(create_image_chosen_avatar=chosen_avatar)

        available_levels = [model.level for model in chosen_avatar.models]
        model_level = await ModelsRepo(db).get_one_field('level', id=image.model_id)
        if model_level in available_levels:
            selected_model_level = model_level
        else:
            selected_model_level = None

        print(f'{image.image_url=}')

        image_file = await self.bot.session._session.get(image.image_url)
        await self.bot.send_photo(
            chat_id=user_id,
            photo=BufferedInputFile(await image_file.read(), filename='result.jpg'),
            caption=texts.generation.pre_create_image(
                prompt=image.prompt,
                has_images=bool(image.prompt_images),
                chosen_avatar_name=chosen_avatar.name
            ),
            reply_markup=keyboards.pre_generate_image(
                has_prompt=bool(image.prompt),
                has_images=bool(image.prompt_images),
                chosen_avatar=chosen_avatar,
                texts=texts,
                selected_model_level=selected_model_level,
                selected_ratio=AspectRatio(image.ratio) if image.ratio else AspectRatio.default()
            )
        )