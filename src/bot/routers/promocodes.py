from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from bot import keyboards
from bot.keyboards import PromocodeCallback
from bot.states.promo_codes import PromocodesStates
from database import PromocodesRepo, db_connect
from database.repositories.promocodes import UsedPromocodesRepo
from depends import payments_service
from enums.payments import PaymentTypeEnum
from sqlalchemy.ext.asyncio import AsyncSession
from texts import Texts

router = Router()


@router.callback_query(PromocodeCallback.filter())
async def promocode(call: CallbackQuery, callback_data: PromocodeCallback,
                    state: FSMContext):
    await call.message.answer(
        text='Введите промокод:',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text='Передумал', callback_data='delete-this-message'
            )]
        ])
    )
    await state.set_state(PromocodesStates.get_promocode)


@router.message(PromocodesStates.get_promocode)
@db_connect()
async def get_promoocode(
    m: Message, state: FSMContext, db: AsyncSession,
    texts: Texts
):
    promocode = await PromocodesRepo(db).get_one(code=m.text)
    if promocode is None:
        await m.answer('Такой промокод не существует')
        return

    if await UsedPromocodesRepo(db).exists(promocode_code=m.text, user_id=m.from_user.id):
        await m.answer('Вы уже активировали этот промокод')
        return

    await m.answer(f'Промокод <b>{promocode.code}</b> на <b>{promocode.sale_percentage}%</b> активирован',
                   reply_markup=keyboards.buy_by_promocode(
                       texts=texts, type=PaymentTypeEnum(promocode.type),
                       sale=promocode.sale_percentage,
                       simple_price=payments_service.models[0].price,
                       portrait_price=payments_service.models[1].price,
                       generations=await payments_service.get_image_packages()
                   ))

    await UsedPromocodesRepo(db).add(promocode_code=m.text, user_id=m.from_user.id)