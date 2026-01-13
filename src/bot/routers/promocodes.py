from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from bot.keyboards import PaymentStartCallback

router = Router()


@router.callback_query(PaymentStartCallback.filter())
async def promocode(call: CallbackQuery, callback_data: PaymentStartCallback):
    await call.message.answer(
        text='Введите промокод:',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text='Передумал', callback_data='delete-this-message'
            )]
        ])
    )