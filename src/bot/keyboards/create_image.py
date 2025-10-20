from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot.keyboards.callback_datas.create_image import SelectedAvatarForGenCallback, StartImageGenCallback, \
    SelectIsPrivateCallback
from schemas.avatars import AvatarSchema
from texts import Texts


def pre_generate_image(
    has_prompt: bool,
    has_images: bool,
    chosen_avatar: AvatarSchema,
    texts: Texts
):
    ikb = [
        # [InlineKeyboardButton(
        #     text='Добавить промпт' if not has_prompt else 'Изменить промпт'
        # )],
        # [InlineKeyboardButton(
        #     text='Добавить фото' if not has_images else 'Заменить фото'
        # )],
        [InlineKeyboardButton(
            text=texts.generation.selected_avatar_button(chosen_avatar.name),
            callback_data=SelectedAvatarForGenCallback(avatar_id=chosen_avatar.id).pack()
        )],
        [InlineKeyboardButton(
            text=texts.generation.is_private_button(is_private=False),
            callback_data=SelectIsPrivateCallback(is_private=False).pack()
        )]
    ]
    if has_images or has_prompt:
        ikb.append([InlineKeyboardButton(
            text=texts.generation.GENERATE_BUTTON, callback_data=StartImageGenCallback().pack()
        )])
    return InlineKeyboardMarkup(inline_keyboard=ikb)