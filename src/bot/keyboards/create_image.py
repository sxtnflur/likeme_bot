from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot.keyboards.callback_datas.create_image import SelectedAvatarForGenCallback, StartImageGenCallback, \
    SelectIsPrivateCallback, SelectModelCallback
from schemas.avatars import AvatarSchema, AvatarWithModelsSchema
from texts import Texts


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
    selected_model_level: int | None = None
):
    if selected_model_level is None:
        levels = list(map(lambda x: x.level, chosen_avatar.models))
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
        ]
    ]
    if has_images or has_prompt:
        ikb.append([InlineKeyboardButton(
            text=texts.generation.GENERATE_BUTTON, callback_data=StartImageGenCallback().pack()
        )])
    return InlineKeyboardMarkup(inline_keyboard=ikb)