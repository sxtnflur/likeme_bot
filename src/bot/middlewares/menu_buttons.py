from typing import Callable, Awaitable, cast

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from texts.base import get_main_menu_button
from ..routers.payment import buy_start
from ..routers.avatar import create_simple_avatar
from ..routers.create_image import create_image


class MenuButtonsMiddleware(BaseMiddleware):
    def __init__(self):
        self.menu_buttons = {
            k: get_main_menu_button(k)
            for k in ['CREATE_IMAGE', 'PAYMENT']
        }
        self.funcs = {
            # 'AVATAR': create_simple_avatar,
            'PAYMENT': buy_start,
            'CREATE_IMAGE': create_image
        }

    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, ...]], Awaitable[...]],
            event: TelegramObject,
            data: dict[str, ...],
    ):
        if not isinstance(event, Message) or not event.text:
            return await handler(event, data)

        cast(event, Message)

        for key, texts in self.menu_buttons.items():
            if event.text in texts:
                return await self.funcs[key](event, state=data.get('state'),
                                             texts=data.get('texts'))

        return await handler(event, data)