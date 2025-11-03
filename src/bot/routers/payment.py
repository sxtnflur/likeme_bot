from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from bot import keyboards
from bot.keyboards import PaymentStartCallback
from config import settings
from database import db_connect, UsersRepo
from depends import payment_factory, payments_service
from sqlalchemy.ext.asyncio import AsyncSession
from texts.base import get_main_menu_button, Texts

router = Router()


@router.message(F.text.in_(get_main_menu_button('PAYMENT')))
@db_connect()
async def buy_start(
    m: Message, state: FSMContext,
    texts: Texts,
    db: AsyncSession
):
    my_image_generations = await UsersRepo(db).get_one_field(
        field='image_generations', id=m.from_user.id
    )
    await m.answer(
        texts.payment.buy_start(my_image_generations=my_image_generations),
        reply_markup=keyboards.start_buy(texts)
    )


@router.callback_query(PaymentStartCallback.filter())
@db_connect()
async def buy_start_call(
    call: CallbackQuery, texts: Texts, db: AsyncSession
):
    my_image_generations = await UsersRepo(db).get_one_field(
        field='image_generations', id=call.from_user.id
    )
    await call.message.edit_text(
        texts.payment.buy_start(my_image_generations=my_image_generations),
        reply_markup=keyboards.start_buy(texts)
    )


@router.callback_query(keyboards.callback_datas.BuyImageGenerationsCallback.filter())
async def buy_image_gens(
    call: CallbackQuery, texts: Texts
):
    packages = await payments_service.get_image_packages()
    await call.message.edit_text(
        texts.payment.BUY_IMAGE_GENERATIONS,
        reply_markup=keyboards.image_packages_list(
            pieces=packages, texts=texts
        )
    )


@router.callback_query(keyboards.callback_datas.SelectImageGenerationsCallback.filter())
async def select_image_generations(
    call: CallbackQuery, texts: Texts,
    callback_data: keyboards.callback_datas.SelectImageGenerationsCallback
):
    package = await payments_service.get_image_package(callback_data.id)
    pay_data = await payment_factory.create_payment(
        amount=package.price,
        description=texts.payment.generation_buy_choose_button(package),
        test=settings.PAYMENT_TEST,
        session=call.bot.session._session,
        metadata={
            'type': 'package',
            'package_id': package.id,
            'user_id': call.from_user.id
        }
    )
    await call.message.edit_text(
        texts.payment.select_package(package),
        reply_markup=keyboards.image_package(
            pay_url=pay_data.url, texts=texts
        )
    )


@router.callback_query(keyboards.callback_datas.BuyModelCallback.filter())
async def buy_model(
    call: CallbackQuery, texts: Texts,
    callback_data: keyboards.callback_datas.BuyModelCallback
):
    pay_data = await payment_factory.create_payment(
        amount=payments_service.model_level_1_price,
        description='Покупка модели Portrait',
        test=settings.PAYMENT_TEST,
        session=call.bot.session._session,
        metadata={
            'type': 'model',
            'model_level': callback_data.level,
            'avatar_id': callback_data.avatar_id,
            'user_id': call.from_user.id
        }
    )
    await call.message.answer(
        texts.payment.buy_model_level_1(price=payments_service.model_level_1_price),
        reply_markup=keyboards.buy_model_level_1(pay_url=pay_data.url, texts=texts)
    )


