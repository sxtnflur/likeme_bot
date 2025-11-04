from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from bot.utils.set_commands import set_commands
from config import settings
from redis.asyncio import Redis

bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
storage = RedisStorage(redis=Redis.from_url(settings.REDIS_URL))
dp = Dispatcher(storage=storage)


async def onstartup(bot: Bot) -> None:
    try:
        await bot.delete_webhook()
    except: pass
    await set_commands(bot)