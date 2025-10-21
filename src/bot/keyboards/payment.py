from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from schemas.payment import ImageGenerationsBuy
from texts import Texts
from .base import create_list_kb
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


def buy_model_level_1(pay_url: str, texts: Texts):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=texts.payment.PAY_BUTTON,
            url=pay_url
        )]
    ])
