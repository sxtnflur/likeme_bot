import os.path
from pathlib import Path

from config import settings
from .base import BaseTexts, AvatarTexts, PaymentTexts, GenerationTexts, MainMenuButtons, ChainMessagesTexts


class Texts:
    def __init__(self, language: str):
        base_dir = Path(settings.BASE_DIR)
        self.folder = base_dir.joinpath(f'texts/texts/{language}')

    def __get_path(self, filename: str):
        return self.folder.joinpath(filename).__str__()

    @property
    def base(self):
        return BaseTexts(self.__get_path('base.json'))

    @property
    def avatar(self):
        return AvatarTexts(self.__get_path('avatar.json'))

    @property
    def payment(self):
        return PaymentTexts(self.__get_path('payment.json'))

    @property
    def generation(self):
        return GenerationTexts(self.__get_path('generation.json'))

    @property
    def main_menu_buttons(self):
        path = self.__get_path('main_menu_buttons.json')
        if not os.path.exists(path):
            Exception('Нет файла main_menu_buttons.json')
        return MainMenuButtons(path)

    @property
    def chain_messages(self):
        return ChainMessagesTexts(self.__get_path('chain_messages.json'))