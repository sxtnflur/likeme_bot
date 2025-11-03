from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import InlineKeyboardMarkup
from pydantic import BaseModel
from bot.loader import bot
from texts import Texts


class SendMessage(BaseModel):
    text: str | None = None
    photo: str | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    state: State | str | None = None

    class Config:
        arbitrary_types_allowed = True

    async def send(self, chat_id: int, state: FSMContext, texts: Texts | None = None):
        if texts:
            if self.text:
                self.text = getattr(texts.chain_messages, self.text)
            if self.reply_markup:
                for row in self.reply_markup.inline_keyboard:
                    for btn in row:
                        btn.text = getattr(texts.chain_messages, btn.text)

        if self.photo:
            await bot.send_photo(
                chat_id=chat_id,
                photo=self.photo,
                caption=self.text,
                reply_markup=self.reply_markup
            )
        elif self.text:
            await bot.send_message(
                chat_id=chat_id,
                text=self.text,
                reply_markup=self.reply_markup
            )
        if self.state:
            await state.set_state(self.state)