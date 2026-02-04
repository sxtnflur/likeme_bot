from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.screens.base import ScreenDef
from texts import Texts


def no_avatar_else(texts: Texts):
    return ScreenDef(
        text='''
Чтобы сделать ремикс, нужен аватар 👤

Он создаётся один раз и используется во всех идеях.

<b>🎁 Бонус для старта</b>
Ты получишь бесплатные генерации, чтобы сразу попробовать REMIX
''',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Что такое REMIX ME?', callback_data='chain-messages:0')],
                    [InlineKeyboardButton(text='Создать аватар', callback_data='chain-messages:2')]]
                )
    )
