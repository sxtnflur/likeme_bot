import json
import re
from functools import lru_cache
from typing import Callable


def camelcase_to_snakecase(text: str) -> str:
    return re.sub(r"([a-z])([A-Z])", r"\1_\2", text).lower()


class TextsJsonMetaClass(type):
    @lru_cache
    def _get_all_data(self) -> dict:
        __filepath__ = object.__getattribute__(self, "__filepath__")
        try:
            with open(__filepath__, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise Exception(
                f"Ошибка при получении данных из: {__filepath__}: {e}"
            )

    def __getattribute__(self, item) -> str | Callable:
        if item == "__filepath__":
            try:
                return object.__getattribute__(self, item)
            except AttributeError:
                return camelcase_to_snakecase(object.__name__)

        # Сначала пробуем получить атрибут обычным способом
        try:
            attr = object.__getattribute__(self, item)
            # Если это метод или функция - возвращаем как есть
            if callable(attr) or isinstance(attr, (classmethod, staticmethod)) or item.startswith('__'):
                return attr
        except AttributeError as e:
            pass

        # Ищем в JSON данных
        all_data = object.__getattribute__(self, '_get_all_data')()
        res = all_data.get(item)
        if not res:
            # Если не нашли в данных, пробуем получить как обычный атрибут
            return object.__getattribute__(self, item)
        return res


class TextsCollectionJson:
    __filepath__: str

    def __init__(self, filename: str):
        self.__filepath__ = filename

    @lru_cache
    def _get_all_data(self) -> dict:
        __filepath__ = object.__getattribute__(self, "__filepath__")
        try:
            with open(__filepath__, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise Exception(
                f"Ошибка при получении данных из: {__filepath__}: {e}"
            )

    def __getattribute__(self, item) -> str | Callable:
        if item == "__filepath__":
            try:
                return object.__getattribute__(self, item)
            except AttributeError:
                return camelcase_to_snakecase(object.__name__)

        # Сначала пробуем получить атрибут обычным способом
        try:
            attr = object.__getattribute__(self, item)
            # Если это метод или функция - возвращаем как есть
            if callable(attr) or isinstance(attr, (classmethod, staticmethod)) or item.startswith('__'):
                return attr
        except AttributeError:
            pass

        # Ищем в JSON данных
        all_data = object.__getattribute__(self, '_get_all_data')()
        res = all_data.get(item)
        if not res:
            # Если не нашли в данных, пробуем получить как обычный атрибут
            return object.__getattribute__(self, item)
        return res