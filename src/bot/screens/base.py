import dataclasses

import aiogram
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, Message, CallbackQuery, InputMediaPhoto, \
    ReplyKeyboardRemove, InputFile
from typing_extensions import Literal
from .. import loader


@dataclasses.dataclass
class ScreenDef:
    text: str | None = None
    photo: str | InputFile | None = None
    document: str | InputFile | None = None
    media_group: list[InputMediaPhoto] | None = None
    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | None = None
    state: str | State | None = None

    @staticmethod
    def __get_fsm(bot_id: int, user_id: int):
        return FSMContext(storage=loader.storage,
                          key=StorageKey(bot_id=bot_id, chat_id=user_id, user_id=user_id))

    async def answer(self, event: Message | CallbackQuery,
                     type_send: Literal['simple', 'del_msg', 'del_rm', 'edit', 'edit_caption'] = 'simple'
                     ):
        if self.state is not None:
            await self.__get_fsm(event.bot.id, event.from_user.id).set_state(self.state)

        if isinstance(event, Message):
            try:
                if type_send in ('del_msg', 'edit'):
                    await event.delete()
                elif type_send == 'del_rm':
                    await event.delete_reply_markup()
            except:
                pass

            if self.photo is not None:
                return await event.answer_photo(
                    photo=self.photo, caption=self.text, reply_markup=self.reply_markup
                )
            elif self.media_group:
                self.media_group[0].caption = self.text
                return await event.answer_media_group(
                    media=self.media_group
                )
            elif self.document:
                return await event.answer_document(
                    document=self.document,
                    caption=self.text,
                    reply_markup=self.reply_markup
                )
            else:
                return await event.answer(
                    text=self.text,
                    reply_markup=self.reply_markup
                )
        else:
            if type_send not in ('edit', 'edit_caption'):
                return await self.answer(event.message, type_send)
            try:
                if self.photo:
                    if type_send == 'edit_caption' and (event.message.photo or event.message.document):
                        try:
                            await event.message.edit_caption(
                                caption=self.text,
                                reply_markup=self.reply_markup
                            )
                        except:
                            return await self.answer(event.message, 'del_msg')
                    else:
                        return await self.answer(event.message, 'del_msg')

                elif event.message.photo:
                    return await self.answer(event.message, type_send)
                elif self.document:
                    if type_send == 'edit_caption' and (event.message.photo or event.message.document):
                        try:
                            await event.message.edit_caption(
                                caption=self.text,
                                reply_markup=self.reply_markup
                            )
                        except:
                            return await self.answer(event.message, 'del_msg')
                    else:
                        return await self.answer(event.message, 'del_msg')
                else:
                    await event.message.edit_text(
                        text=self.text,
                        reply_markup=self.reply_markup
                    )
            except:
                return await self.answer(event.message, type_send)

    async def send_by_id(self, user_id: int, bot: aiogram.Bot):
        if self.state is not None:
            await self.__get_fsm(bot.id, user_id).set_state(self.state)

        if self.photo:
            return await bot.send_photo(
                chat_id=user_id,
                photo=self.photo, caption=self.text,
                reply_markup=self.reply_markup
            )
        elif self.media_group:
            self.media_group[0].caption = self.text
            return await bot.send_media_group(
                chat_id=user_id,
                media=self.media_group
            )
        else:
            return await bot.send_message(
                chat_id=user_id,
                text=self.text, reply_markup=self.reply_markup
            )