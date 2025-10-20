from typing import Optional

from aiogram.filters.callback_data import CallbackData


class SelectedAvatarForGenCallback(CallbackData, prefix='selected-avatar-for-gen-image'):
    avatar_id: int


class StartImageGenCallback(CallbackData, prefix='start-gen-image'):
    ...


class SelectIsPrivateCallback(CallbackData, prefix='pregen-select-private'):
    is_private: bool = False

    @classmethod
    def from_callback_data(cls, callback_data: str) -> Optional['SelectIsPrivateCallback']:
        prefix = 'pregen-select-private'
        if not callback_data.startswith(prefix):
            return
        is_private = bool(int(callback_data.split(':')[1]))
        return SelectIsPrivateCallback(is_private=is_private)