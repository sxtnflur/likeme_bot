from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, URLInputFile, WebAppInfo
from bot import states
from bot.screens.base import ScreenDef
from config import settings
from texts import Texts


def didnot_load_photos_in_begin(texts: Texts):
    return ScreenDef(
        text='''
<b>🚀 В ленте — 1152+ идей от других пользователей!

📸 Отправь своё фото, чтобы начать ремиксить в нашей ленте!</b>
''',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text='Создать аватар',
                callback_data='chain-messages:2'
            )],
            [InlineKeyboardButton(
                text='Открыть ленту', web_app=WebAppInfo(url=settings.WEBAPP_URL)
            )]
        ]),
        state=states.NanobananaAvatarStates.send_photo
    )


def created_avatar_didnot_generations(texts: Texts, user_name: str,
                                      image_url: str,
                                      remix_it_url: str):
    return ScreenDef(
        photo=URLInputFile(url=image_url),
        text=f'''
<b>✨ Оцени новую идею от пользователя {user_name}</b>!

Пока тебя не было, в ленте <b>REMIX ME</b> появилось много стилей!

<b>🔥 Сделай ремикс!</b>
''',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text='REMIX IT!', url=remix_it_url
            )],
            [InlineKeyboardButton(
                text='Открыть ленту', web_app=WebAppInfo(url=settings.WEBAPP_URL)
            )]
        ])
    )