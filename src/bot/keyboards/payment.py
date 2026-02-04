from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from enums.payments import PaymentTypeEnum
from schemas.payment import ImageGenerationsBuy
from texts import Texts
from . import LoadPhotosToModelCallback, AvatarsListCallback
from .base import create_list_kb
from .callback_datas import BuyAvatarCallback, StartFillAddedAvatarCallback
from .callback_datas.payment import PaymentStartCallback, SelectImageGenerationsCallback, \
    PromocodeCallback


def start_buy(texts: Texts):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=texts.payment.BUY_IMAGE_GENERATIONS_BUTTON,
            callback_data=PaymentStartCallback().pack()
        )]
    ])


def image_packages_list(pieces: list[ImageGenerationsBuy], texts: Texts,
                        save_msg: bool = False):
    kb = create_list_kb(
        objs=pieces,
        get_btn=lambda piece: InlineKeyboardButton(
            text=texts.payment.generation_buy_choose_button(piece),
            callback_data=SelectImageGenerationsCallback(id=piece.id,
                                                         save_msg=save_msg).pack()
        ),
        width=1
    )
    return InlineKeyboardMarkup(inline_keyboard=kb)


def pay_url_kb(pay_url: str, texts: Texts,
               back_callback_data: str | None = None):
    ikb = [[InlineKeyboardButton(
        text=texts.payment.PAY_BUTTON,
        url=pay_url
    )],
        # [InlineKeyboardButton(
        #     text=texts.payment.PROMOCODE_BUTTON,
        #     callback_data=PromocodeCallback().pack()
        # )]
    ]

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
        )],
        [InlineKeyboardButton(
            text=texts.base.BACK_BUTTON,
            callback_data=AvatarsListCallback().pack()
        )]
    ])


def buy_by_promocode(
    texts: Texts,
    type: PaymentTypeEnum,
    sale: int,
    *,
    simple_price: int,
    portrait_price: int,
    generations: list[ImageGenerationsBuy]
):
    def count_price(price: int):
        return round(price * (1 - sale / 100))

    for g in generations:
        g.price = count_price(g.price)

    btns = {
        'simple-avatar': InlineKeyboardButton(
            text='Аватар Simple ({} руб)'.format(count_price(simple_price)),
            callback_data=BuyAvatarCallback(level=0).pack()
        ),
        'portrait-avatar': InlineKeyboardButton(
            text='Аватар Portrait ({} руб)'.format(count_price(portrait_price)),
            callback_data=BuyAvatarCallback(level=1).pack()
        ),
        'generations': image_packages_list(generations, texts, save_msg=True).inline_keyboard
    }

    ikb: list[list[InlineKeyboardButton]] | None = None
    if type == PaymentTypeEnum.any:
        ikb = (
            [[btns['simple-avatar'], btns['portrait-avatar']],
             *btns['generations']]
        )
    elif type == PaymentTypeEnum.generations:
        ikb = (btns['generations'])
    elif type == PaymentTypeEnum.avatar:
        ikb = ([
            [btns['simple-avatar']],
            [btns['portrait-avatar']]
        ])
    elif type == PaymentTypeEnum.avatar_simple:
        ikb = [
            [btns['simple-avatar']]
        ]
    elif type == PaymentTypeEnum.avatar_portrait:
        ikb = [[btns['portrait-avatar']]]
    if ikb is not None:
        print(f'{ikb=}')
        return InlineKeyboardMarkup(inline_keyboard=ikb)