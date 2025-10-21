from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from bot import keyboards
from bot.states import NanobananaAvatarStates
from database import AvatarsRepo, db_connect
from depends import avatars_service
from sqlalchemy.ext.asyncio import AsyncSession
from texts.base import Texts

router = Router()


@router.message(NanobananaAvatarStates.send_photo, F.photo)
@db_connect()
async def create_simple_avatar(
    m: Message, state: FSMContext,
    texts: Texts, db: AsyncSession
):
    file_id = m.photo[-1].file_id
    await state.update_data(nano_avatar_id=file_id)

    if not await AvatarsRepo(db).exists(user_id=m.from_user.id, name=m.from_user.full_name):
        reply_markup = keyboards.input_simple_avatar_name(texts)
    else:
        reply_markup = None

    await m.delete()
    await m.answer_photo(
        photo=file_id,
        caption=texts.avatar.ON_SEND_AVATAR_PHOTO,
        reply_markup=reply_markup
    )
    await state.set_state(NanobananaAvatarStates.send_name)


@router.message(NanobananaAvatarStates.send_name)
@db_connect()
async def get_name_for_simple_avatar(
    m: Message, state: FSMContext,
    db: AsyncSession,
    texts: Texts
):
    file_id = await state.get_value('nano_avatar_id')
    avatar_name = m.text.strip()
    await state.clear()
    await avatars_service.add_simple_avatar(
        user_id=m.from_user.id,
        file_id=file_id,
        name=avatar_name,
        db=db
    )
    await m.answer(
        texts.avatar.on_create_avatar(avatar_name)
    )


@router.callback_query(keyboards.callback_datas.InputMyNameForAvatarCallback.filter(F.type == 'simple'))
@db_connect()
async def input_my_name_for_avatar(
    call: CallbackQuery, state: FSMContext,
    db: AsyncSession, texts: Texts
):
    file_id = await state.get_value('nano_avatar_id')
    avatar_name = call.from_user.full_name
    await avatars_service.add_simple_avatar(
        user_id=call.from_user.id,
        file_id=file_id,
        name=avatar_name,
        db=db
    )
    await call.message.answer(
        texts.avatar.on_create_avatar(avatar_name),
        reply_markup=keyboards.on_create_avatar(texts)
    )