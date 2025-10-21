from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot import keyboards
from bot.middlewares.media_group import MediaMiddleware
from bot.states import NanobananaAvatarStates
from config import settings
from database import db_connect, UsersRepo
from depends import users_service
from services.ai.fal import upload_zip_by_file_ids
from sqlalchemy.ext.asyncio import AsyncSession
from texts import Texts, get_texts
from database.repositories import AvatarsRepo

router = Router()
# router.message.middleware(MediaMiddleware(4))
#
#
# @router.message(F.photo)
# async def get_test_photos(m: Message, media_group: list[Message] = None):
#     print(f'{len(media_group)=}')
#     zip_url = await upload_zip_by_file_ids(
#         file_ids=list(map(lambda x: x.photo[-1].file_id, media_group)),
#         user_id=m.from_user.id,
#         bot=m.bot
#     )
#     print(f'{zip_url=}')


@router.message(CommandStart())
@db_connect()
async def start(
    m: Message, state: FSMContext,
    db: AsyncSession
):
    await state.clear()
    language = await UsersRepo(db).get_one_field('language', id=m.from_user.id)
    if not language:
        if m.from_user.language_code in settings.ENABLE_LANGUAGES:
            language = m.from_user.language_code
        else:
            language = settings.DEFAULT_LANGUAGE

    # user_exists = await UsersRepo(db).exists(id=m.from_user.id)
    user_has_avatar = await AvatarsRepo(db).exists(user_id=m.from_user.id)

    await users_service.add_user_from_aiogram(user=m.from_user, language=language, db=db)
    texts = get_texts(language)

    if user_has_avatar:
        await m.answer(
            texts.base.START_MESSAGE,
            reply_markup=keyboards.main_menu(texts)
        )
    else:
        await m.answer(
            texts.base.FIRST_MESSAGE
        )
        await state.set_state(NanobananaAvatarStates.send_photo)
