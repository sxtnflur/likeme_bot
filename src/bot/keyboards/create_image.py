from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CopyTextButton, WebAppInfo
from bot.keyboards.callback_datas.create_image import SelectedAvatarForGenCallback, StartImageGenCallback, \
    SelectIsPrivateCallback, SelectModelCallback, SelectAvatarForGenCallback, BackToCreatingImageCallback, \
    SelectRatioCallback, SwitchIsPrivateCreatedImageCallback
from config import settings
from enums.generation import AspectRatio
from schemas.avatars import AvatarSchema, AvatarWithModelsSchema
from texts import Texts
from .base import create_list_kb


def start_create_image(texts: Texts):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=texts.generation.FEED_BUTTON,
            web_app=WebAppInfo(url=settings.WEBAPP_URL)
        )]
    ])


def to_create_image(texts: Texts):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=texts.generation.GENERATE_BUTTON,
            callback_data='create_image'
        )]
    ])


def pre_generate_image(
    has_prompt: bool,
    has_images: bool,
    chosen_avatar: AvatarWithModelsSchema,
    texts: Texts,
    selected_model_level: int | None = None,
    selected_ratio: AspectRatio = AspectRatio.default()
):
    if selected_model_level is None:
        levels = list(map(lambda x: x.level, chosen_avatar.models))
        if not levels:
            raise Exception(f'У аватара {chosen_avatar.id} нет моделей (models={chosen_avatar.models})')
        selected_model_level = max(levels)

    ikb = [
        [InlineKeyboardButton(
            text=texts.generation.selected_avatar_button(chosen_avatar.name),
            callback_data=SelectedAvatarForGenCallback(avatar_id=chosen_avatar.id).pack()
        )],
        [InlineKeyboardButton(
            text=texts.generation.is_private_button(is_private=False),
            callback_data=SelectIsPrivateCallback(is_private=False).pack()
        )],
        [
            InlineKeyboardButton(
                text=texts.avatar.get_model_level_name(level=model.level,
                                                       mark_as_chosen=model.level == selected_model_level),
                callback_data=SelectModelCallback(
                    level=model.level,
                    is_selected=model.level == selected_model_level
                ).pack()
            )
            for model in chosen_avatar.models
        ],
        [InlineKeyboardButton(
            text=texts.generation.get_text_btn_ratio(selected_ratio),
            callback_data=SelectRatioCallback(ratio=selected_ratio).pack()
        )]
    ]
    print(f'{ikb[-1]=}')
    if has_images or has_prompt:
        ikb.insert(0, [InlineKeyboardButton(
            text=texts.generation.GENERATE_BUTTON, callback_data=StartImageGenCallback().pack()
        )])
    return InlineKeyboardMarkup(inline_keyboard=ikb)


def select_avatar_for_gen(avatars: list[AvatarSchema], texts: Texts):
    ikb = create_list_kb(
        objs=avatars,
        get_btn=lambda x: InlineKeyboardButton(
            text=x.name, callback_data=SelectAvatarForGenCallback(avatar_id=x.id).pack()
        )
    )
    ikb.append([InlineKeyboardButton(
        text=texts.base.BACK_BUTTON, callback_data=BackToCreatingImageCallback().pack()
    )])
    return InlineKeyboardMarkup(inline_keyboard=ikb)


def on_generated_image(image_id: int, is_private: bool, texts: Texts,
                       can_create_avatar: bool | None = None):
    ikb = [InlineKeyboardButton(
            text=texts.generation.switch_is_private_button(is_private),
            callback_data=SwitchIsPrivateCreatedImageCallback(image_id=image_id).pack()
        )]
    if can_create_avatar is None:
        pass
    elif can_create_avatar:
        ikb.append([
            InlineKeyboardButton(
                text='Создать аватар', callback_data='create_new_avatar'
            )
        ])
    else:
        ikb.append([
            InlineKeyboardButton(
                text='Купить аватар', callback_data='buy_new_avatar'
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=ikb)