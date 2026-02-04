import asyncio
from contextlib import asynccontextmanager

from aiogram.types import Update
from api.app import create_app
from bot.exceptions import register_errors
from bot.middlewares import MenuButtonsMiddleware
from bot.middlewares.texts import TextsMiddleware
from config import settings
from fastapi import FastAPI, Request, BackgroundTasks
from log import logger
from bot.loader import bot, dp
from bot.register import onstartup, onshutdown
from bot.routers import __routers__

dp.include_routers(*__routers__)
dp.message.middleware(TextsMiddleware())
dp.callback_query.middleware(TextsMiddleware())

dp.message.middleware(MenuButtonsMiddleware())
register_errors(dp)

dp.shutdown.register(onshutdown)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await onstartup(bot)
    await bot.set_webhook(url=settings.BOT_WEBHOOK_URL, request_timeout=60)
    yield
    await bot.delete_webhook()


def create_webhook(_=None) -> FastAPI:
    app = create_app(prefix=settings.API_PREFIX, lifespan=lifespan)

    async def feed_update(update: Update):
        await dp.feed_update(bot=bot, update=update)

    @app.post(settings.BOT_WEBHOOK_ENDPOINT)
    async def bot_webhook(request: Request, bg_tasks: BackgroundTasks):
        update = Update.model_validate(await request.json(), context={"bot": bot})
        bg_tasks.add_task(feed_update, update)
    return app


async def start_polling() -> None:
    await onstartup(bot)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(start_polling())