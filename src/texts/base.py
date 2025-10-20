from config import settings
from .collections.main import Texts


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


PAG_BTN_LEFT = '⏪'
PAG_BTN_RIGHT = '⏩'