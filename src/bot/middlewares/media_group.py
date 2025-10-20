import asyncio
from typing import *
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery


class MediaMiddleware(BaseMiddleware):
    def __init__(self, latency: Union[int, float] = 0.01):
        self.medias = {}
        self.latency = latency
        super(MediaMiddleware, self).__init__()

    async def __call__(
        self,
        handler: Callable[[Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:

        if isinstance(event, Message) and event.media_group_id:
            try:
                self.medias[event.media_group_id].append(event)
                return
            except KeyError:
                self.medias[event.media_group_id] = [event]
                await asyncio.sleep(self.latency)

                data["media_group"] = self.medias.pop(event.media_group_id)

        return await handler(event, data)