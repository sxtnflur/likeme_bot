from aiogram import Dispatcher
from aiogram.exceptions import TelegramAPIError
from aiogram.types import InlineKeyboardMarkup, Message, ErrorEvent


class SendToUserException(Exception):
    text: str

    def __init__(self,
                 text: str, reply_markup: InlineKeyboardMarkup | None = None,
                 add_support: bool = False,
                 base_exc: Exception | None = None
                 ):
        self.base_exc = base_exc
        self.text = text
        self.reply_markup = reply_markup

        if add_support:
            self.text += '\n\nПоддержка: @teledeff_support'

    def __str__(self):
        text = self.text
        if self.base_exc:
            text += f' (Ориг. ошибка: {self.base_exc})'
        return text

    def __repr__(self):
        return self.__str__()


async def callback(event: ErrorEvent):
    chat_id = event.update.event.from_user.id
    exc = event.exception
    if isinstance(exc, SendToUserException):
        await event.update.bot.send_message(
            chat_id,
            text=exc.text,
            reply_markup=exc.reply_markup
        )
    elif isinstance(exc, TelegramAPIError):
        await event.update.bot.send_message(
            chat_id,
            text='Произошла ошибка при работе с Telegram. Попробуйте позже'
        )
    else:
        await event.update.bot.send_message(
            chat_id,
            text='Произошла непредвиденная ошибка. Мы уже работает над этим'
        )
    raise exc


def register_errors(dp: Dispatcher):
    dp.error.register(callback)