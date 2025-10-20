import textwrap

from config import settings
from schemas.payment import GenerationsBuy
from .collections.main import Texts
from .json import TextsCollectionJson


# class Texts(TextsCollectionJson):
#     BACK_BUTTON: str
#
#     START_MESSAGE: str
#
#     ON_SEND_AVATAR_PHOTO: str
#     ON_CREATE_AVATAR: str
#     ON_IMAGE_GENERATED: str
#
#     # Generate
#     START_CREATE_IMAGE: str
#     PRE_CREATE_IMAGE: str
#     IMAGE_GENERATION_WAIT_MSG: str
#     NO_GENERATIONS_MORE: str
#     NO_AVATAR_ELSE: str
#
#     INPUT_MY_NAME_FOR_MODEL: str
#
#     UNPREDICTABLE_ERROR: str
#
#     BUY_START: str
#     BUY_IMAGE_GENERATIONS_BUTTON: str
#     BUY_IMAGE_GENERATIONS: str
#     BUY_IMAGE_GENERATIONS_CHOOSE_BUTTON: str = '{} за {} руб'
#
#     SELECT_PACKAGE: str
#
#     PAY_BUTTON: str = 'Оплатить'
#     ON_SUCCESS_PAYMENT: str
#
#     def buy_start(self, my_image_generations: int):
#         return self.BUY_START.format(my_image_generations)
#
#     def generation_buy_choose_button(self, obj: GenerationsBuy):
#         return self.BUY_IMAGE_GENERATIONS_CHOOSE_BUTTON.format(
#             obj.generations, obj.price
#         )
#
#     def select_package(self, obj: GenerationsBuy):
#         return self.SELECT_PACKAGE
#
#     def pre_create_image(
#         self, prompt: str,
#         has_images: bool,
#         chosen_avatar_name: str
#     ):
#         # Промпт: {}
#         # Фото: {}
#         #
#         # Можешь присылать фото или промпт для генерации
#         # или жми Генерировать
#
#         has_prompt_text = textwrap.shorten(text=prompt, width=15)
#         has_images_text = 'V' if has_images else 'X'
#         return self.PRE_CREATE_IMAGE.format(
#             has_prompt_text, has_images_text, chosen_avatar_name
#         )


def get_texts(language: str) -> Texts:
    return Texts(language)


def get_all_texts():
    texts: dict[str, Texts] = {language: Texts(language) for language in settings.ENABLE_LANGUAGES}
    return texts


def get_main_menu_button(key: str):
    res = []
    for lang, texts in get_all_texts().items():
        res.append(getattr(texts.main_menu_buttons, key))
    return res


BACK_BUTTON = '↩ Назад'


PAG_BTN_LEFT = '⏪'
PAG_BTN_RIGHT = '⏩'