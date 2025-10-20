from aiogram.filters.callback_data import CallbackData
from typing_extensions import Literal


class InputMyNameForAvatarCallback(CallbackData, prefix='input-my-name-for-avatar'):
    type: Literal['simple'] = 'simple'