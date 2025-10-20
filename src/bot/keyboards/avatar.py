from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.keyboards.callback_datas.avatar import InputMyNameForAvatarCallback
from texts import Texts


def input_simple_avatar_name(texts: Texts):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=texts.avatar.INPUT_MY_NAME_FOR_MODEL,
            callback_data=InputMyNameForAvatarCallback().pack()
        )]
    ])


def on_create_avatar(texts: Texts):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=texts.avatar.TO_CREATE_IMAGE_BUTTON,
            callback_data='create_image'
        )]
    ])