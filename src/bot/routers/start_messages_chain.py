from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from bot.utils.simple_send_message import SendMessage
from texts import Texts
from ..states.avatar import NanobananaAvatarStates

chain_messages: list[SendMessage] = [
    SendMessage(text='MESSAGE_1',
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='NEXT_BUTTON_1', callback_data='chain-messages:1'),
                     InlineKeyboardButton(text='CREATE_AVATAR_BUTTON', callback_data='chain-messages:3')]]
                )
                ),
    SendMessage(text='MESSAGE_2',
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(
                        text='NEXT_BUTTON_2', callback_data='chain-messages:2'
                    )]
                ])),
    SendMessage(text='MESSAGE_3',
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(
                        text='NEXT_BUTTON_3', callback_data='chain-messages:3'
                    )]
                ])),
    SendMessage(text='MESSAGE_4',
                state=NanobananaAvatarStates.send_photo)
]

router = Router()


@router.callback_query(F.data.startswith('chain-messages:'))
async def chain_messages_handle(
        call: CallbackQuery, state: FSMContext, texts: Texts
):
    chain_messages_index = int(call.data.split(':')[1])
    message = chain_messages[chain_messages_index]
    await message.send(chat_id=call.message.chat.id, state=state, texts=texts)
