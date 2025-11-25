from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from bot.routers.create_image import get_prompt
from bot.routers.start import start
from database import db_connect, AvatarsRepo
from sqlalchemy.ext.asyncio import AsyncSession
from texts import Texts
from .start_messages_chain import chain_messages
from ..middlewares.media_group import MediaMiddleware
from ..utils.delete_msgs import delete_saved_msgs

router = Router()
router.message.middleware(MediaMiddleware(2))


@router.message()
@db_connect()
async def handle_message(m: Message, db: AsyncSession, state: FSMContext,
                         texts: Texts, media_group: list[Message] | None = None):
    avatars = await AvatarsRepo(db).exists(user_id=m.from_user.id, status='ready')
    if not avatars:
        user_has_in_progress_avatar = await AvatarsRepo(db).exists(user_id=m.from_user.id, status='in_progress')
        if user_has_in_progress_avatar:
            await m.answer(
                text=texts.avatar.WAIT_MSG_CREATE_AVATAR
            )
        else:
            await chain_messages[-1].send(chat_id=m.from_user.id, state=state, texts=texts)
        return

    await get_prompt(m=m, state=state, texts=texts, db=db)


@router.message(F.photo & F.caption == 'fileid')
async def get_photo(m: Message):
    await m.answer(f'FILE ID: <code>{m.photo[-1].file_id}</code>', parse_mode='HTML')


@router.callback_query(F.data == 'delete-this-message')
async def delete_this_message(call: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    await call.message.delete()


@router.callback_query()
async def get_call(call: CallbackQuery):
    await call.answer(cache_time=3)