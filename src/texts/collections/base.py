import textwrap

from config import settings
from database import models
from enums import ModelStatusType
from enums.generation import AspectRatio
from schemas.avatars import AvatarSchema
from schemas.payment import GenerationsBuy
from texts.json import TextsCollectionJson
from typing_extensions import Literal


class BaseTexts(TextsCollectionJson):
    BACK_BUTTON: str
    START_MESSAGE: str
    FIRST_MESSAGE: str
    UNPREDICTABLE_ERROR: str
    FEED_MESSAGE: str
    SUPPORT_MESSAGE: str

    def feed_message(self, feed_url):
        return self.FEED_MESSAGE.format(feed_url)


class AvatarTexts(TextsCollectionJson):
    WAIT_MSG_CREATE_AVATAR: str
    WAIT_MSG_CREATE_AVATAR_PRO: str
    ON_SEND_AVATAR_PHOTO: str
    ON_SEND_AVATAR_PHOTO_IF_CAN_TAKE_ACCOUNT_NAME: str
    ON_CREATE_AVATAR: str
    INPUT_MY_NAME_FOR_MODEL: str

    TO_CREATE_IMAGE_BUTTON: str

    AVATARS_LIST: str
    AVATARS_LIST_WITH_NEW_AVATARS: bool
    AVATAR_PAGE: str
    BUY_LEVEL_1_BUTTON: str

    SELECT_AVATAR_TO_BUY_PRO: str
    NO_AVATARS: str

    BUY_AVATAR_BUTTON: str
    CREATE_AVATAR_BUTTON: str

    def avatars_list(self, has_new_avatars: bool):
        if has_new_avatars:
            return self.AVATARS_LIST_WITH_NEW_AVATARS
        else:
            return self.AVATARS_LIST

    def on_send_avatar_photo(self, can_take_account_name: bool):
        if can_take_account_name:
            return self.ON_SEND_AVATAR_PHOTO_IF_CAN_TAKE_ACCOUNT_NAME
        else:
            return self.ON_SEND_AVATAR_PHOTO

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
            text = '✅ ' + text
        return text

    def get_model_status(self, status: ModelStatusType):
        if status == 'added':
            return 'Ожидает настройки'
        elif status == 'training':
            return 'Обучается... ⏳'
        else:
            return 'Готов ✅'

    def avatar_page(self, avatar: AvatarSchema) -> str:
        return self.AVATAR_PAGE.format(
            name=avatar.name or '-',
            status=self.get_model_status(avatar.status),
            model=self.get_model_level_name(avatar.level)
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

    YOU_HAVE_ONLY_ONE_AVATAR: str
    # MODEL: str
    SHOWN_AVATARS_WITH_MODEL: str
    YOU_DONT_HAVE_SUCH_AVATARS: str
    AVATAR_NOT_AVAILABLE_NOW: str
    MODEL_NOT_AVAILABLE_NOW: str

    FEED_BUTTON: str

    SWITCH_IS_PRIVATE_BUTTON_PRIVATE: str
    SWITCH_IS_PRIVATE_BUTTON_PUBLIC: str


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

    def after_image_generated(self, is_private: bool, webapp_post_url: str, remix_url: str):
        if is_private:
            return (
                'Твоя генерация в <b>приватном режиме</b> 🔒, ее никто не увидит, если ты сам этого не '
                'захочешь\n\n'
                'Но ты все равно можешь отправить эту <a href="{}">ссылку</a> на свою генерацию '
                'друзьям:\n<code>{}</code>\n\n'
                'По ней они смогут поставить <b>лайк</b>, <b>поделиться</b> и <b>повторить твой промпт</b> на себе\n\n'
                'Если ты хочешь только дать возможность посмотреть фото и повторить промпт, '
                'тебе нужна вот эта <a href="{}">ссылка</a>: <code>{}</code>'
            ).format(webapp_post_url, webapp_post_url, remix_url, remix_url)
        else:
            return (
                'Делись своей <a href="{}">генерацией</a> с друзьями: <code>{}</code>\n\n'
                'И может поискать свой пост в <a href="{}">ленте</a>'
            ).format(webapp_post_url, webapp_post_url, settings.WEBAPP_DIRECT_URL)

    def get_text_btn_ratio(self, ratio: AspectRatio) -> str:
        names = {
            AspectRatio.square: 'Квадрат',
            AspectRatio.high_1: 'Портрет',
            AspectRatio.high_2: 'Вертик. - Instagram',
            AspectRatio.high_3: 'Вертик. - Facebook',
            AspectRatio.high_4: 'Вертик - Stories/Reels',
            AspectRatio.wide_1: 'Горизонт. - Классика',
            AspectRatio.wide_2: 'Горизонт. - Чуть шире',
            AspectRatio.wide_3: 'Full HD',
            AspectRatio.wide_4: 'Кинематограф'
        }
        name = names.get(ratio)
        w, h = ratio.get_aspects()
        return f'{w}:{h} ({name})'

    def switch_is_private_button(self, is_private) -> str:
        if is_private:
            return self.SWITCH_IS_PRIVATE_BUTTON_PUBLIC
        else:
            return self.SWITCH_IS_PRIVATE_BUTTON_PRIVATE


class PaymentTexts(TextsCollectionJson):
    BUY_START: str
    BUY_IMAGE_GENERATIONS_BUTTON: str
    BUY_IMAGE_GENERATIONS: str
    BUY_IMAGE_GENERATIONS_CHOOSE_BUTTON: str
    BUY_AVATAR: str
    PAY_AVATAR: str

    SELECT_PACKAGE: str

    PAY_BUTTON: str
    ON_SUCCESS_PAYMENT: str
    ON_SUCCESS_PAYMENT_PACKAGE: str

    BUY_LEVEL_1: str

    def buy_start(self, my_image_generations: int):
        return self.BUY_START.format(my_image_generations)

    def generation_buy_choose_button(self, obj: GenerationsBuy):
        return self.BUY_IMAGE_GENERATIONS_CHOOSE_BUTTON.format(
            obj.generations, obj.price
        )

    def select_package(self, obj: GenerationsBuy):
        return self.SELECT_PACKAGE

    def pay_avatar(self, price: int) -> str:
        return self.BUY_AVATAR.format(price)

    def buy_model_level_1(self, price: int) -> str:
        return self.BUY_LEVEL_1.format(price)

    def on_success_payment_package(self, gens: int) -> str:
        return self.ON_SUCCESS_PAYMENT_PACKAGE.format(gens)


class ChainMessagesTexts(TextsCollectionJson):
    MESSAGE_1: str
    MESSAGE_2: str
    MESSAGE_3: str
    MESSAGE_4: str
    NEXT_BUTTON_1: str
    NEXT_BUTTON_2: str
    NEXT_BUTTON_3: str
    CREATE_AVATAR_BUTTON: str


class MainMenuButtons(TextsCollectionJson):
    AVATAR: str
    CREATE_IMAGE: str
    PAYMENT: str
    FEED: str
    SUPPORT: str