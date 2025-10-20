from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from bot.utils.set_commands import set_commands
from config import settings

bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher()


async def onstartup(bot: Bot) -> None:
    await bot.delete_webhook()
    await set_commands(bot)