import copy

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import InlineKeyboardMarkup, InputFile, InputFileUnion
from pydantic import BaseModel
from bot.loader import bot
from texts import Texts


class SendMessage(BaseModel):
    text: str | None = None
    photo: InputFileUnion | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    state: State | str | None = None

    class Config:
        arbitrary_types_allowed = True

    async def send(self, chat_id: int, state: FSMContext, texts: Texts | None = None):
        text = None
        reply_markup = None
        if texts:
            if self.text:
                text = getattr(texts.chain_messages, self.text)
            if self.reply_markup:
                reply_markup = copy.deepcopy(self.reply_markup)
                for row in reply_markup.inline_keyboard:
                    for btn in row:
                        btn.text = getattr(texts.chain_messages, btn.text)
        else:
            text = self.text

        if self.photo:
            await bot.send_photo(
                chat_id=chat_id,
                photo=self.photo,
                caption=text,
                reply_markup=reply_markup
            )
        elif self.text:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup
            )
        if self.state:
            await state.set_state(self.state)