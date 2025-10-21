from aiogram.filters.callback_data import CallbackData
from typing_extensions import Literal
from .base import ScrollingCallback


class InputMyNameForAvatarCallback(CallbackData, prefix='input-my-name-for-avatar'): ...


class AvatarsListCallback(ScrollingCallback, prefix='avatars-list'): ...


class SelectAvatarCallback(CallbackData, prefix='select-avatar'):
    avatar_id: int


class LoadPhotosToModelCallback(CallbackData, prefix='load-photos-to-model'):
    model_id: int