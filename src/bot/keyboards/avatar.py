from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.keyboards.base import create_scrolling_kb
from bot.keyboards.callback_datas.avatar import (
    InputMyNameForAvatarCallback, AvatarsListCallback, SelectAvatarCallback, LoadPhotosToModelCallback
)
from .callback_datas.payment import BuyModelCallback
from schemas.avatars import AvatarSchema, Model
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


def avatars_list(
    avatars: list[AvatarSchema], page: int = 0, limit: int = 10
) -> InlineKeyboardMarkup:
    return create_scrolling_kb(
        page=page,
        objs=avatars,
        callback_data=AvatarsListCallback,
        get_btn=lambda avatar: InlineKeyboardButton(
            text=avatar.name,
            callback_data=SelectAvatarCallback(avatar_id=avatar.id).pack()
        ),
        limit=limit
    )


def avatar_page(
    texts: Texts,
    avatar_id: int,
    models: list[Model]
) -> InlineKeyboardMarkup:
    ikb = []
    model_lvl1 = list(filter(lambda x: x.level == 1, models))
    if not model_lvl1:
        ikb.append([
            InlineKeyboardButton(
                text=texts.avatar.BUY_LEVEL_1_BUTTON,
                callback_data=BuyModelCallback(avatar_id=avatar_id, level=1).pack()
            )
        ])
    elif model_lvl1:
        model_lvl1 = model_lvl1[0]
        if model_lvl1.status == 'paid':
            ikb.append([
                InlineKeyboardButton(
                    text='Загрузить мои фото в Portrait',
                    callback_data=LoadPhotosToModelCallback(model_id=model_lvl1.id).pack()
                )
            ])

    ikb.append([
        InlineKeyboardButton(
            text=texts.base.BACK_BUTTON,
            callback_data=AvatarsListCallback().pack()
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=ikb)
