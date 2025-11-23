from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from database import db_connect, AvatarsRepo
from sqlalchemy.ext.asyncio import AsyncSession
from ..states.avatar import NanobananaAvatarStates, CreateModelStates

router = Router()


@router.callback_query(F.data == 'create_new_avatar')
@db_connect()
async def create_new_avatar(
    call: CallbackQuery, db: AsyncSession, state: FSMContext
):
    user_empty_avatar = await AvatarsRepo(db).get_one(
        user_id=call.from_user.id, model_data=None
    )
    if user_empty_avatar is None:
        ...
    else:
        if user_empty_avatar.level == 0:
            await call.message.answer(
                'Отправь 1 фото'
            )
            await state.set_state(NanobananaAvatarStates.send_photo)
        elif user_empty_avatar.level == 1:
            await call.message.answer(
                'Отправь 10 фото'
            )
            await state.set_state(CreateModelStates.send_photos)
