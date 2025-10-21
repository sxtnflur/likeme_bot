import textwrap

from schemas.avatars import AvatarWithModelsSchema
from schemas.payment import GenerationsBuy
from texts.json import TextsCollectionJson
from typing_extensions import Literal


class BaseTexts(TextsCollectionJson):
    BACK_BUTTON: str
    START_MESSAGE: str
    FIRST_MESSAGE: str
    UNPREDICTABLE_ERROR: str


class AvatarTexts(TextsCollectionJson):
    ON_SEND_AVATAR_PHOTO: str
    ON_CREATE_AVATAR: str
    INPUT_MY_NAME_FOR_MODEL: str

    TO_CREATE_IMAGE_BUTTON: str

    AVATARS_LIST: str
    AVATAR_PAGE: str
    BUY_LEVEL_1_BUTTON: str

    def on_create_avatar(self, avatar_name: str):
        return self.ON_CREATE_AVATAR.format(avatar_name)

    def get_model_level_name(self, level: Literal[0, 1], mark_as_chosen: bool = False) -> str:
        if level == 0:
            text = 'Simple'
        elif level == 1:
            text = 'Portrait'
        else:
            raise ValueError('level не может быть {}'.format(level))
        if mark_as_chosen:
            text = 'V ' + text
        return text

    def avatar_page(self, avatar: AvatarWithModelsSchema) -> str:
        available_levels = [model.level for model in avatar.models]
        return self.AVATAR_PAGE.format(
            name=avatar.name,
            models='\n'.join([
                self.get_model_level_name(level)
                + ' ✅' if level in available_levels else ' ❌'
                for level in (0, 1)
            ])
        )


class GenerationTexts(TextsCollectionJson):
    START_CREATE_IMAGE: str
    PRE_CREATE_IMAGE: str
    ON_IMAGE_GENERATED: str
    NO_GENERATIONS_MORE: str
    NO_AVATAR_ELSE: str

    SELECTED_AVATAR_BUTTON: str

    IS_PRIVATE_BUTTON_PRIVATE: str
    IS_PRIVATE_BUTTON_PUBLIC: str

    GENERATE_BUTTON: str

    ON_FAILED_GENERATION: str

    WAIT_MESSAGE: str

    def selected_avatar_button(self, avatar_name: str):
        return self.SELECTED_AVATAR_BUTTON.format(avatar_name)

    def pre_create_image(
        self, prompt: str,
        has_images: bool,
        chosen_avatar_name: str
    ):
        # Промпт: {}
        # Фото: {}
        #
        # Можешь присылать фото или промпт для генерации
        # или жми Генерировать

        has_prompt_text = textwrap.shorten(text=prompt, width=50, placeholder='...')
        has_images_text = '✅' if has_images else '...'
        return self.PRE_CREATE_IMAGE.format(
            has_prompt_text, has_images_text, chosen_avatar_name
        )

    def is_private_button(self, is_private: bool) -> str:
        if is_private:
            return self.IS_PRIVATE_BUTTON_PRIVATE
        return self.IS_PRIVATE_BUTTON_PUBLIC

    def wait_message(self, prompt: str, is_private: bool) -> str:
        return self.WAIT_MESSAGE.format(
            prompt=textwrap.shorten(text=prompt, width=50, placeholder='...'),
            privacy=self.is_private_button(is_private)
        )

    def on_image_generated(self, prompt: str, is_private: bool):
        return self.ON_IMAGE_GENERATED.format(
            prompt=textwrap.shorten(text=prompt, width=50, placeholder='...'),
            privacy=self.is_private_button(is_private)
        )


class PaymentTexts(TextsCollectionJson):
    BUY_START: str
    BUY_IMAGE_GENERATIONS_BUTTON: str
    BUY_IMAGE_GENERATIONS: str
    BUY_IMAGE_GENERATIONS_CHOOSE_BUTTON: str = '{} за {} руб'

    SELECT_PACKAGE: str

    PAY_BUTTON: str = 'Оплатить'
    ON_SUCCESS_PAYMENT: str

    BUY_LEVEL_1: str

    def buy_start(self, my_image_generations: int):
        return self.BUY_START.format(my_image_generations)

    def generation_buy_choose_button(self, obj: GenerationsBuy):
        return self.BUY_IMAGE_GENERATIONS_CHOOSE_BUTTON.format(
            obj.generations, obj.price
        )

    def select_package(self, obj: GenerationsBuy):
        return self.SELECT_PACKAGE

    def buy_model_level_1(self, price: int) -> str:
        return self.BUY_LEVEL_1.format(price)


class MainMenuButtons(TextsCollectionJson):
    AVATAR: str
    CREATE_IMAGE: str
    PAYMENT: str