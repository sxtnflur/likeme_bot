from aiogram import Bot
from bot.utils.set_commands import set_commands
from depends import bg_tasks_factory


async def onstartup(bot: Bot) -> None:
    try:
        await bot.delete_webhook()
    except: pass
    await set_commands(bot)
    print('start')
    await bg_tasks_factory.start()
    print('started')


async def onshutdown(bot: Bot) -> None:
    await bg_tasks_factory.shutdown()