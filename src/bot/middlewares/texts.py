from typing import Callable, Awaitable

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject
from texts import get_texts
from database import db_connect, UsersRepo
from sqlalchemy.ext.asyncio import AsyncSession


async def get_language(user_id: int) -> str:
    @db_connect()
    async def get_language_(user_id: int, db: AsyncSession) -> str:
        return await UsersRepo(db).get_one_field('language', id=user_id)
    return await get_language_(user_id)


class TextsMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, ...]], Awaitable[...]],
            event: TelegramObject,
            data: dict[str, ...],
    ):
        state: FSMContext = data.get('state')
        lang = await state.get_value('language', None)
        if not lang:
            lang = await get_language(user_id=event.from_user.id)
            await state.update_data(language=lang)
        texts = get_texts(language=lang)
        data['texts'] = texts
        data['language'] = lang
        return await handler(event, data)