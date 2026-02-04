from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from bot import keyboards
from bot.screens.base import ScreenDef
from config import settings
from texts import Texts


def on_successful_payment_package(texts: Texts, generations: int):
    return ScreenDef(
        text=texts.payment.on_success_payment_package(generations),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=texts.main_menu_buttons.CREATE_IMAGE, callback_data='create_image'
            )],
            [InlineKeyboardButton(
                text=texts.generation.FEED_BUTTON, web_app=WebAppInfo(url=settings.WEBAPP_URL)
            )]
        ])
    )


def on_success_payment_avatar(texts: Texts, avatar_id: int):
    return ScreenDef(
        text=texts.payment.ON_SUCCESS_PAYMENT_AVATAR,
        reply_markup=keyboards.on_success_payment_avatar(texts, avatar_id)
    )