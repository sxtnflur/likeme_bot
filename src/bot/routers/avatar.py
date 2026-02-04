from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from bot import keyboards
from bot.exceptions import SendToUserException, NoBoughtAvatarsException
from bot.keyboards import BuyAvatarCallback, StartFillAddedAvatarCallback
from bot.middlewares.media_group import MediaMiddleware
from bot.routers.start_messages_chain import chain_messages
from bot.states import NanobananaAvatarStates, CreateModelStates
from config import settings
from database import AvatarsRepo, db_connect, UsersRepo, OrdersRepo
from depends import avatars_service, payment_factory, payments_service
from enums.payments import PaymentTypeEnum
from schemas.avatars import AvatarSchema
from services.payment import models
from sqlalchemy.ext.asyncio import AsyncSession
from texts.base import Texts, get_main_menu_button

router = Router()
router.message.middleware(MediaMiddleware(1))


@router.message(F.text.in_(get_main_menu_button('AVATAR')))
@db_connect()
async def start_avatars(
    m: Message,
    texts: Texts,
    db: AsyncSession
):
    avatars = await AvatarsRepo(db).get_list(
        filters=dict(user_id=m.from_user.id),
        offset=0,
        limit=10
    )
    await m.answer(
        texts.avatar.avatars_list(has_new_avatars=any([1 for i in avatars if i.status != 'ready'])),
        reply_markup=keyboards.avatars_list(
            texts=texts,
            avatars=avatars,
            page=0,
            limit=10
        )
    )


@router.callback_query(keyboards.callback_datas.AvatarsListCallback.filter())
@db_connect()
async def avatars_list(
        call: CallbackQuery, callback_data: keyboards.callback_datas.AvatarsListCallback,
        texts: Texts,
        db: AsyncSession
):
    avatars = await AvatarsRepo(db).get_list(
        filters=dict(user_id=call.from_user.id),
        offset=callback_data.page * callback_data.limit,
        limit=callback_data.limit
    )

    if call.message.photo:
        await call.message.delete()
        await call.message.answer(
            texts.avatar.avatars_list(has_new_avatars=any([1 for i in avatars if i.status != 'ready'])),
            reply_markup=keyboards.avatars_list(
                texts=texts,
                avatars=list(map(AvatarSchema.model_validate, avatars)),
                page=callback_data.page,
                limit=callback_data.limit
            )
        )
    else:
        await call.message.edit_text(
            texts.avatar.avatars_list(has_new_avatars=any([1 for i in avatars if i.status != 'ready'])),
            reply_markup=keyboards.avatars_list(
                texts=texts,
                avatars=list(map(AvatarSchema.model_validate, avatars)),
                page=callback_data.page,
                limit=callback_data.limit
            )
        )


@router.callback_query(keyboards.callback_datas.SelectAvatarCallback.filter())
@db_connect()
async def select_avatar(
    call: CallbackQuery,
    callback_data: keyboards.callback_datas.SelectAvatarCallback,
    texts: Texts,
    db: AsyncSession
):
    print(f'{callback_data.avatar_id=}')
    avatar = await AvatarsRepo(db).get_one(id=callback_data.avatar_id)
    print(f'{avatar=}')
    await call.message.edit_text(
        texts.avatar.avatar_page(avatar),
        reply_markup=keyboards.avatar_page(
            texts=texts, avatar=avatar
        )
    )


@router.message(NanobananaAvatarStates.send_photo, F.photo)
@db_connect()
async def create_simple_avatar(
    m: Message, state: FSMContext,
    texts: Texts, db: AsyncSession
):
    file_id = m.photo[-1].file_id
    await state.update_data(nano_avatar_id=file_id)

    if not await AvatarsRepo(db).exists(user_id=m.from_user.id, name=m.from_user.full_name):
        reply_markup = keyboards.input_avatar_name(texts, level=0)
        text = texts.avatar.ON_SEND_AVATAR_PHOTO_IF_CAN_TAKE_ACCOUNT_NAME
    else:
        reply_markup = None
        text = texts.avatar.ON_SEND_AVATAR_PHOTO

    await m.delete()
    await m.answer_photo(
        photo=file_id,
        caption=text,
        reply_markup=reply_markup
    )
    await state.set_state(NanobananaAvatarStates.send_name)


@router.message(NanobananaAvatarStates.send_name)
@db_connect()
async def get_name_for_simple_avatar(
    m: Message, state: FSMContext,
    db: AsyncSession,
    texts: Texts
):
    if not m.text:
        await m.answer('Отправьте только текст')
        return

    avatar_name = m.text.strip()

    if await AvatarsRepo(db).exists(user_id=m.from_user.id, name=avatar_name):
        await m.answer('Аватар с таким названием у вас уже есть. Введите другое название:')
        return

    data = await state.get_data()
    file_id = data.get('nano_avatar_id')
    await state.clear()

    inputed_avatar_id: int | None = data.get('inputed_avatar_id')
    if not inputed_avatar_id:
        inputed_avatar_id = await AvatarsRepo(db).get_one_field(
            field='id', user_id=m.from_user.id, status='added', level=0
        )

    wait_msg = await m.answer(texts.avatar.WAIT_MSG_CREATE_AVATAR)
    await avatars_service.train_simple_avatar(
        user_id=m.from_user.id,
        file_id=file_id,
        avatar_id=inputed_avatar_id,
        name=avatar_name,
        db=db
    )
    await wait_msg.delete()
    await m.answer(
        '🎉',
        reply_markup=keyboards.main_menu(texts)
    )
    await m.answer(
        texts.avatar.on_create_avatar(avatar_name),
        reply_markup=keyboards.on_create_avatar(texts)
    )


@router.callback_query(keyboards.callback_datas.InputMyNameForAvatarCallback.filter(F.level == 0))
@db_connect()
async def input_my_name_for_avatar(
    call: CallbackQuery, state: FSMContext,
    db: AsyncSession, texts: Texts
):
    data = await state.get_data()
    file_id = data.get('nano_avatar_id')
    avatar_name = call.from_user.full_name

    inputed_avatar_id: int | None = data.get('inputed_avatar_id')
    if not inputed_avatar_id:
        inputed_avatar_id = await AvatarsRepo(db).get_one_field(
            field='id', user_id=call.from_user.id, status='added', level=0
        )
        if not inputed_avatar_id:
            raise NoBoughtAvatarsException

    wait_msg = await call.message.answer(texts.avatar.WAIT_MSG_CREATE_AVATAR)
    await avatars_service.train_simple_avatar(
        user_id=call.from_user.id,
        file_id=file_id,
        avatar_id=inputed_avatar_id,
        name=avatar_name,
        db=db
    )
    await wait_msg.delete()
    await call.message.answer(
        '🎉',
        reply_markup=keyboards.main_menu(texts)
    )
    await call.message.answer(
        texts.avatar.on_create_avatar(avatar_name),
        reply_markup=keyboards.on_create_avatar(texts)
    )


@router.callback_query(keyboards.callback_datas.LoadPhotosToModelCallback.filter())
async def load_photos_to_model(
    call: CallbackQuery,
    callback_data: keyboards.callback_datas.LoadPhotosToModelCallback,
    texts: Texts,
    state: FSMContext
):
    await call.message.answer(
        'Отправьте ваши 10 фото'
    )
    await state.update_data(model_id=callback_data.model_id)
    await state.set_state(CreateModelStates.send_photos)


@router.message(CreateModelStates.send_photos)
@db_connect()
async def get_photos_to_model(
    m: Message,
    texts: Texts,
    state: FSMContext,
    db: AsyncSession,
    media_group: list[Message] = None
):
    if not media_group or len(media_group) < 10:
        if not media_group:
            if m.photo:
                count_photos = 1
            else:
                count_photos = 0
        else:
            count_photos = len(media_group)
        await m.answer(
            'Вы отправили только {} фото вместо 10. Пожалуйста, отправьте заново 10 фото одним сообщением'
            .format(count_photos)
        )
        return

    inputed_avatar_id = await state.get_value('inputed_avatar_id')
    if not inputed_avatar_id:
        inputed_avatar_id = await AvatarsRepo(db).get_one_field(
            field='id', user_id=m.from_user.id, status='added', level=1
        )
        if not inputed_avatar_id:
            raise NoBoughtAvatarsException

    if not await AvatarsRepo(db).exists(user_id=m.from_user.id, name=m.from_user.full_name):
        reply_markup = keyboards.input_avatar_name(texts, level=1)
        text = texts.avatar.ON_SEND_AVATAR_PHOTO_IF_CAN_TAKE_ACCOUNT_NAME
    else:
        reply_markup = None
        text = texts.avatar.ON_SEND_AVATAR_PHOTO

    await state.update_data(portrait_file_ids=list(map(lambda x: x.photo[-1].file_id, media_group)))
    await m.answer(
        text=text, reply_markup=reply_markup
    )
    await state.set_state(CreateModelStates.send_name)


@router.message(CreateModelStates.send_name, F.text)
@db_connect()
async def get_model_name_portait(m: Message, state: FSMContext, db: AsyncSession, texts: Texts):
    data = await state.get_data()
    portrait_file_ids = data.get('portrait_file_ids')
    inputed_avatar_id: int | None = data.get('inputed_avatar_id')
    avatar_name = m.text.strip()

    if await AvatarsRepo(db).exists(user_id=m.from_user.id, name=avatar_name):
        await m.answer('У вас уже есть аватар с таким названием. Ведите другое название')
        return

    if not inputed_avatar_id:
        inputed_avatar_id = await AvatarsRepo(db).get_one_field(
            field='id', user_id=m.from_user.id, status='added', level=0
        )
        if not inputed_avatar_id:
            raise NoBoughtAvatarsException

    await m.answer(texts.avatar.WAIT_MSG_CREATE_AVATAR_PRO)
    await avatars_service.start_train_portrait_avatar(
        file_ids=portrait_file_ids,
        user_id=m.from_user.id,
        avatar_id=inputed_avatar_id,
        avatar_name=avatar_name,
        db=db
    )


@router.callback_query(keyboards.callback_datas.InputMyNameForAvatarCallback.filter(F.level == 1))
@db_connect()
async def input_my_name_for_portait_avatar(
    call: CallbackQuery, state: FSMContext,
    db: AsyncSession, texts: Texts
):
    data = await state.get_data()
    portrait_file_ids = data.get('portrait_file_ids')
    avatar_name = call.from_user.full_name

    inputed_avatar_id: int | None = data.get('inputed_avatar_id')
    if not inputed_avatar_id:
        inputed_avatar_id = await AvatarsRepo(db).get_one_field(
            field='id', user_id=call.from_user.id, status='added', level=1
        )
        if not inputed_avatar_id:
            raise NoBoughtAvatarsException

    await call.message.answer(texts.avatar.WAIT_MSG_CREATE_AVATAR_PRO)
    await avatars_service.start_train_portrait_avatar(
        user_id=call.from_user.id,
        file_ids=portrait_file_ids,
        avatar_id=inputed_avatar_id,
        avatar_name=avatar_name,
        db=db
    )


@router.callback_query(F.data == 'buy_new_avatar')
async def buy_new_avatar(
    call: CallbackQuery, texts: Texts
):
    await call.message.delete()
    await call.message.answer_photo(
        photo=FSInputFile(settings.BASE_DIR + '/files/images/buy_avatar.jpg'),
        caption=texts.payment.BUY_AVATAR,
        reply_markup=keyboards.buy_avatar(
            texts=texts, simple_price=models.get(0).price, portrait_price=models.get(1).price
        )
    )


@router.callback_query(BuyAvatarCallback.filter())
@db_connect()
async def buy_avatar_select_model(
    call: CallbackQuery, callback_data: BuyAvatarCallback,
    texts: Texts, *, db: AsyncSession | None = None
):

    model = payments_service.get_model_info(callback_data.level)
    order_id = await OrdersRepo(db).add_and_get(
        dict(user_id=call.from_user.id),
        get_field='id'
    )
    pay_data = await payment_factory.create_payment(
        amount=model.price,
        description=model.payment_description,
        session=call.bot.session._session,
        metadata=dict(
            user_id=call.from_user.id,
            model_level=model.level,
            type='avatar',
            order_id=order_id.hex
        )
    )
    await call.message.delete()
    await call.message.answer(
        texts.payment.SELECT_PACKAGE,
        reply_markup=keyboards.pay_url_kb(
            pay_url=pay_data.url, texts=texts,
            back_callback_data='buy_new_avatar'
        )
    )


@router.callback_query(StartFillAddedAvatarCallback.filter())
@db_connect()
async def start_fill_added_avatar(
    call: CallbackQuery,
    callback_data: StartFillAddedAvatarCallback,
    db: AsyncSession,
    state: FSMContext,
    texts: Texts
):
    print('start_fill_added_avatar')
    avatar_level = await AvatarsRepo(db).get_one_field('level', id=callback_data.avatar_id)
    print(f'{avatar_level=}')
    await state.update_data(inputed_avatar_id=callback_data.avatar_id)
    if avatar_level == 0:
        await chain_messages[-1].send(chat_id=call.message.chat.id, state=state, texts=texts)
    elif avatar_level == 1:
        await call.message.answer(
            'Отправьте ваши 10 фото'
        )
        await state.set_state(CreateModelStates.send_photos)