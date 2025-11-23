from aiogram.filters.callback_data import CallbackData
from typing_extensions import Literal
from .base import ScrollingCallback


class InputMyNameForAvatarCallback(CallbackData, prefix='input-my-name-for-avatar'):
    level: int


class AvatarsListCallback(ScrollingCallback, prefix='avatars-list'): ...


class SelectAvatarCallback(CallbackData, prefix='select-avatar'):
    avatar_id: int


class LoadPhotosToModelCallback(CallbackData, prefix='load-photos-to-model'):
    model_id: int


class BuyAvatarCallback(CallbackData, prefix='buy-avatar'):
    level: int


class StartFillAddedAvatarCallback(CallbackData, prefix='start-fill-added-avatar'):
    avatar_id: int