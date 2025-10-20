from aiogram.filters.callback_data import CallbackData


class SelectedAvatarForGenCallback(CallbackData, prefix='selected-avatar-for-gen-image'):
    avatar_id: int


class StartImageGenCallback(CallbackData, prefix='start-gen-image'):
    ...