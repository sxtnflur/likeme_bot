from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

router = Router()


@router.message(F.photo)
async def get_photo(m: Message):
    await m.answer(f'FILE ID: <code>{m.photo[-1].file_id}</code>', parse_mode='HTML')


@router.callback_query()
async def get_call(call: CallbackQuery):
    await call.answer(cache_time=3)