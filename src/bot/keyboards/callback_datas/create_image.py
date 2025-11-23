from typing import Optional, Literal

from aiogram.filters.callback_data import CallbackData
from enums.generation import AspectRatio
from schemas.avatars import AvatarStatusType


class SelectedAvatarForGenCallback(CallbackData, prefix='selected-avatar-for-gen-image'):
    avatar_id: int
    level: int = 0


class SelectAvatarForGenCallback(CallbackData, prefix='select-avatar-for-gen'):
    avatar_id: int


class StartImageGenCallback(CallbackData, prefix='start-gen-image'):
    ...


class SelectRatioCallback(CallbackData, prefix='select-ratio-for-gen'):
    ratio: str

    @classmethod
    def from_callback_data(cls, callback_data: str) -> Optional['SelectRatioCallback']:
        prefix = 'select-ratio-for-gen'
        if not callback_data.startswith(prefix):
            return
        ratio = callback_data.split(':')[1]
        return SelectRatioCallback(ratio=ratio)


class SelectIsPrivateCallback(CallbackData, prefix='pregen-select-private'):
    is_private: bool = False

    @classmethod
    def from_callback_data(cls, callback_data: str) -> Optional['SelectIsPrivateCallback']:
        prefix = 'pregen-select-private'
        if not callback_data.startswith(prefix):
            return
        is_private = bool(int(callback_data.split(':')[1]))
        return SelectIsPrivateCallback(is_private=is_private)


class SelectModelCallback(CallbackData, prefix='pregen-select-model'):
    level: int
    is_selected: bool = False

    @classmethod
    def from_callback_data(cls, callback_data: str) -> Optional['SelectModelCallback']:
        prefix = 'pregen-select-model'
        if not callback_data.startswith(prefix):
            return
        level = int(callback_data.split(':')[1])
        is_selected = bool(int(callback_data.split(':')[2]))
        return SelectModelCallback(level=level, is_selected=is_selected)


class BackToCreatingImageCallback(CallbackData, prefix='back-to-creating-image'): ...
class SwitchIsPrivateCreatedImageCallback(CallbackData, prefix='switch-privacy-created-image'):
    image_id: int