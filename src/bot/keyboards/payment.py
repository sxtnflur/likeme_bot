from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from schemas.payment import ImageGenerationsBuy
from texts import Texts
from . import LoadPhotosToModelCallback
from .base import create_list_kb
from .callback_datas import BuyAvatarCallback, StartFillAddedAvatarCallback
from .callback_datas.payment import BuyImageGenerationsCallback, PaymentStartCallback, SelectImageGenerationsCallback


def start_buy(texts: Texts):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=texts.payment.BUY_IMAGE_GENERATIONS_BUTTON,
            callback_data=BuyImageGenerationsCallback().pack()
        )]
    ])


def image_packages_list(pieces: list[ImageGenerationsBuy], texts: Texts):
    kb = create_list_kb(
        objs=pieces,
        get_btn=lambda piece: InlineKeyboardButton(
            text=texts.payment.generation_buy_choose_button(piece),
            callback_data=SelectImageGenerationsCallback(id=piece.id).pack()
        )
    )
    kb.append([
        InlineKeyboardButton(
            text=texts.base.BACK_BUTTON,
            callback_data=PaymentStartCallback().pack()
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=kb)


def image_package(pay_url: str, texts: Texts):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=texts.payment.PAY_BUTTON,
            url=pay_url
        )],
        [InlineKeyboardButton(
            text=texts.base.BACK_BUTTON,
            callback_data=BuyImageGenerationsCallback().pack()
        )]
    ])


def pay_url_kb(pay_url: str, texts: Texts, back_callback_data: str | None = None):
    ikb = [[InlineKeyboardButton(
            text=texts.payment.PAY_BUTTON,
            url=pay_url
        )]]
    if back_callback_data:
        ikb.append([
            InlineKeyboardButton(
                text=texts.base.BACK_BUTTON,
                callback_data=back_callback_data
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=ikb)


def on_success_payment_model(model_id: int, texts: Texts, level: int = 1):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
                    text='Загрузить мои фото в Portrait',
                    callback_data=LoadPhotosToModelCallback(model_id=model_id).pack()
                )]
    ])


def on_success_payment_avatar(texts: Texts, avatar_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text='Создать аватар',
            callback_data=StartFillAddedAvatarCallback(avatar_id=avatar_id).pack()
        )]
    ])


def to_buy_avatar(texts: Texts):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text='Купить аватар', callback_data='buy_new_avatar'
        )]
    ])


def buy_avatar(
    texts: Texts, simple_price: int, portrait_price: int
):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text='Simple - {} руб'.format(simple_price),
            callback_data=BuyAvatarCallback(level=0).pack()
        )],
        [InlineKeyboardButton(
            text='Portrait - {} руб'.format(portrait_price),
            callback_data=BuyAvatarCallback(level=1).pack()
        )]
    ])