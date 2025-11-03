import aiogram
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: aiogram.Bot) -> None:
    await bot.set_my_commands(
        commands=[
            BotCommand(
                command='start', description='Перезапустить бота'
            ),
            BotCommand(
                command='support', description='Поддержка'
            )
        ],
        scope=BotCommandScopeDefault()
    )