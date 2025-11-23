from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot import keyboards
from bot.middlewares.media_group import MediaMiddleware
from bot.routers.start_messages_chain import chain_messages
from bot.states import NanobananaAvatarStates
from config import settings
from database import db_connect, UsersRepo
from depends import users_service, remixing_service, avatars_service
from services.ai.fal import upload_zip_by_file_ids
from sqlalchemy.ext.asyncio import AsyncSession
from texts import Texts, get_texts, get_main_menu_button
from database.repositories import AvatarsRepo

router = Router()


@router.message(CommandStart())
@db_connect()
async def start(
        m: Message, state: FSMContext,
        command: CommandObject,
        db: AsyncSession
):
    await state.clear()

    await users_service.add_user_from_aiogram(user=m.from_user, language=m.from_user.language_code, db=db)
    language = await UsersRepo(db).get_one_field('language', id=m.from_user.id)
    texts = get_texts(language)

    print(f'{command.args=}')
    if command.args:
        if await remixing_service.process_start_link(
            payload=command.args,
            user_id=m.from_user.id,
            texts=texts,
            state=state,
            db=db
        ):
            return

    user_has_avatar = await AvatarsRepo(db).exists(user_id=m.from_user.id)
    if not user_has_avatar:
        await avatars_service.create_avatar(
            user_id=m.from_user.id, level=0, db=db
        )
        await chain_messages[0].send(chat_id=m.from_user.id, state=state, texts=texts)
    else:
        user_has_ready_avatar = await AvatarsRepo(db).exists(user_id=m.from_user.id, status='ready')
        if user_has_ready_avatar:
            await m.answer(
                texts.base.START_MESSAGE,
                reply_markup=keyboards.main_menu(texts)
            )
        else:
            await chain_messages[0].send(chat_id=m.from_user.id, state=state, texts=texts)


@router.message(F.text.in_(get_main_menu_button('FEED')))
async def feed(m: Message, texts: Texts):
    await m.answer(texts.base.feed_message(feed_url=settings.WEBAPP_DIRECT_URL))


@router.message(Command('support'))
async def support(m: Message, texts: Texts):
    await m.answer(texts.base.SUPPORT_MESSAGE)


@router.message(F.text.in_(get_main_menu_button('SUPPORT')))
async def support(m: Message, texts: Texts):
    await m.answer(texts.base.SUPPORT_MESSAGE)

