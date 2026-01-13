from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CopyTextButton, WebAppInfo
from bot.keyboards.callback_datas.create_image import SelectedAvatarForGenCallback, StartImageGenCallback, \
    SelectIsPrivateCallback, SelectModelCallback, SelectAvatarForGenCallback, BackToCreatingImageCallback, \
    SelectRatioCallback, SwitchIsPrivateCreatedImageCallback, EditPromptCallback
from config import settings
from enums.generation import AspectRatio
from schemas.avatars import AvatarSchema
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
    chosen_avatar: AvatarSchema,
    texts: Texts,
    selected_ratio: AspectRatio = AspectRatio.default(),
    is_private: bool = False,
):
    # models = list(filter(lambda x: x.status == 'ready', chosen_avatar.models))
    # levels = list(map(lambda x: x.level, models))
    # if not levels:
    #     raise Exception(f'У аватара {chosen_avatar.id} нет моделей (models={models})')

    # if selected_model_level is None or selected_model_level not in levels:
    #     selected_model_level = max(levels)

    ikb = [
        [InlineKeyboardButton(
            text=texts.generation.EDIT_PROMPT_BUTTON,
            callback_data=EditPromptCallback().pack()
        )],
        [InlineKeyboardButton(
            text=texts.generation.is_private_button(is_private=is_private),
            callback_data=SelectIsPrivateCallback(is_private=is_private).pack()
        )],
        [InlineKeyboardButton(
            text=texts.generation.selected_avatar_button(chosen_avatar.name),
            callback_data=SelectedAvatarForGenCallback(avatar_id=chosen_avatar.id).pack()
        )],
        # [
        #     InlineKeyboardButton(
        #         text=texts.avatar.get_model_level_name(level=model.level,
        #                                                mark_as_chosen=model.level == selected_model_level),
        #         callback_data=SelectModelCallback(
        #             level=model.level,
        #             is_selected=model.level == selected_model_level
        #         ).pack()
        #     )
        #     for model in models
        # ],
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


def select_avatar_for_gen(avatars: list[AvatarSchema], texts: Texts,
                          selected_avatar_id: int, filter_by_level: int = 0):
    ikb = create_list_kb(
        objs=avatars,
        get_btn=lambda x: InlineKeyboardButton(
            text=x.name, callback_data=SelectAvatarForGenCallback(
                avatar_id=x.id
            ).pack()
        )
    )
    ikb.append([
        InlineKeyboardButton(
            text=texts.generation.SHOWN_AVATARS_WITH_MODEL, callback_data='-'
        )
    ])
    ikb.append([
        InlineKeyboardButton(
            text=texts.avatar.get_model_level_name(0, mark_as_chosen=filter_by_level == 0),
            callback_data=SelectedAvatarForGenCallback(avatar_id=selected_avatar_id, level=0).pack()
        ),
        InlineKeyboardButton(
            text=texts.avatar.get_model_level_name(1, mark_as_chosen=filter_by_level == 1),
            callback_data=SelectedAvatarForGenCallback(avatar_id=selected_avatar_id, level=1).pack()
        )
    ])
    ikb.append([InlineKeyboardButton(
        text=texts.base.BACK_BUTTON, callback_data=BackToCreatingImageCallback().pack()
    )])
    return InlineKeyboardMarkup(inline_keyboard=ikb)


def on_generated_image(image_id: int, is_private: bool, texts: Texts):
    ikb = [[InlineKeyboardButton(
            text=texts.generation.switch_is_private_button(is_private),
            callback_data=SwitchIsPrivateCreatedImageCallback(image_id=image_id).pack()
        )]]
    return InlineKeyboardMarkup(inline_keyboard=ikb)


def edit_prompt(texts: Texts):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=texts.base.CHANGED_MIND, callback_data='delete-this-message'
        )]
    ])