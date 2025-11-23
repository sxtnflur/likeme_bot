from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.keyboards.base import create_scrolling_kb
from bot.keyboards.callback_datas.avatar import (
    InputMyNameForAvatarCallback, AvatarsListCallback, SelectAvatarCallback, LoadPhotosToModelCallback,
    StartFillAddedAvatarCallback
)
from .callback_datas.payment import BuyModelCallback
from schemas.avatars import AvatarSchema, Model
from texts import Texts


def input_avatar_name(texts: Texts, level: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=texts.avatar.INPUT_MY_NAME_FOR_MODEL,
            callback_data=InputMyNameForAvatarCallback(level=level).pack()
        )]
    ])


def on_create_avatar(texts: Texts):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=texts.avatar.TO_CREATE_IMAGE_BUTTON,
            callback_data='create_image'
        )]
    ])


def avatars_list(
    texts: Texts,
    avatars: list[AvatarSchema], page: int = 0, limit: int = 10
) -> InlineKeyboardMarkup:
    if avatars:
        rm = create_scrolling_kb(
            page=page,
            objs=avatars,
            callback_data=AvatarsListCallback,
            get_btn=lambda avatar: InlineKeyboardButton(
                text=avatar.name or ('🆕 ' + texts.avatar.get_model_level_name(avatar.level)),
                callback_data=SelectAvatarCallback(avatar_id=avatar.id).pack()
            ),
            limit=limit
        )
        rm.inline_keyboard.append([
            InlineKeyboardButton(
                text=texts.avatar.BUY_AVATAR_BUTTON, callback_data='buy_new_avatar'
            )
        ])
        return rm
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=texts.avatar.BUY_AVATAR_BUTTON, callback_data='buy_new_avatar'
            )]
        ])


def avatar_page(
    texts: Texts,
    avatar: AvatarSchema
) -> InlineKeyboardMarkup:
    ikb = []

    if avatar.status == 'added':
        ikb.append([InlineKeyboardButton(
            text='Настроить',
            callback_data=StartFillAddedAvatarCallback(avatar_id=avatar.id).pack()
        )])

    ikb.append([
        InlineKeyboardButton(
            text=texts.base.BACK_BUTTON,
            callback_data=AvatarsListCallback().pack()
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=ikb)


def pro_avatar_start_know():
    return InlineKeyboardMarkup(inline_keyboard=[
         [InlineKeyboardButton(
            text='Купить', callback_data='buy_pro_avatar'
        )]
    ])
