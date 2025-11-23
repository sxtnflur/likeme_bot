from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from bot import keyboards
from bot.keyboards import BuyModelCallback
from bot.routers.avatar import start_avatars
from bot.routers.payment import buy_model
from database import db_connect, AvatarsRepo, UsersRepo
from schemas.avatars import AvatarSchema
from sqlalchemy.ext.asyncio import AsyncSession
from texts import Texts
from .start_messages_chain import chain_messages

router = Router()


@router.callback_query(F.data == 'pro_avatar')
async def pro_avatar(
    call: CallbackQuery, texts: Texts
):
    await call.message.answer(
        texts.payment.BUY_LEVEL_1,
        reply_markup=keyboards.pro_avatar_start_know()
    )


@router.callback_query(F.data == 'buy_pro_avatar')
@db_connect()
async def pro_avatar_2(
    call: CallbackQuery,
    db: AsyncSession,
    texts: Texts,
    state: FSMContext
):
    avatars = await AvatarsRepo(db).get_list(
        filters=dict(user_id=call.from_user.id)
    )
    if len(avatars) == 0:
        await call.message.answer(texts.avatar.NO_AVATARS)
        await chain_messages[-1].send(
            chat_id=call.message.chat.id,
            state=state,
            texts=texts
        )
        return
    elif len(avatars) == 1:
        avatar = avatars[0]
        await buy_model(
            call=call,
            texts=texts,
            callback_data=BuyModelCallback(avatar_id=avatar.id, level=1)
        )
    else:
        await call.message.answer(
            texts.avatar.SELECT_AVATAR_TO_BUY_PRO,
            reply_markup=keyboards.avatars_list(
                texts=texts,
                avatars=avatars,
                page=0,
                limit=50,
                can_create_avatar=None
            )
        )