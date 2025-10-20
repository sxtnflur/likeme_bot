import os.path
from pathlib import Path

from .base import BaseTexts, AvatarTexts, PaymentTexts, GenerationTexts, MainMenuButtons


class Texts:
    def __init__(self, language: str):
        self.folder = Path(f'./src/texts/texts/{language}')

    def __get_path(self, filename: str):
        return os.path.join(self.folder, filename)

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