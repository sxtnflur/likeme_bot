from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from bot import keyboards
from bot.middlewares.media_group import MediaMiddleware
from bot.routers.start_messages_chain import chain_messages
from bot.states import NanobananaAvatarStates, CreateModelStates
from database import AvatarsRepo, db_connect, ModelsRepo, UsersRepo
from depends import avatars_service, payment_factory, payments_service
from schemas.avatars import AvatarSchema
from sqlalchemy.ext.asyncio import AsyncSession
from texts.base import Texts, get_main_menu_button

router = Router()
router.message.middleware(MediaMiddleware(1))


@router.message(F.text.in_(get_main_menu_button('AVATAR')))
@db_connect()
async def start_avatars(
    m: Message,
    texts: Texts,
    db: AsyncSession,
    state: FSMContext
):
    avatars = await AvatarsRepo(db).get_list(
        filters=dict(user_id=m.from_user.id),
        offset=0,
        limit=50
    )
    avatars = list(map(AvatarSchema.model_validate, avatars))
    if not avatars:
        await m.answer(
            text=texts.base.FIRST_MESSAGE
        )
        await state.set_state(NanobananaAvatarStates.send_photo)
        return

    can_create_avatar = await UsersRepo(db).get_one_field('can_create_avatar', id=m.from_user.id)

    await m.answer(
        texts.avatar.AVATARS_LIST,
        reply_markup=keyboards.avatars_list(
            texts=texts,
            avatars=avatars,
            page=0,
            limit=50,
            can_create_avatar=can_create_avatar
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
    can_create_avatar = await UsersRepo(db).get_one_field('can_create_avatar', id=call.from_user.id)
    await call.message.edit_text(
        texts.avatar.AVATARS_LIST,
        reply_markup=keyboards.avatars_list(
            texts=texts,
            avatars=list(map(AvatarSchema.model_validate, avatars)),
            page=callback_data.page,
            limit=callback_data.limit,
            can_create_avatar=can_create_avatar
        )
    )


@router.callback_query(F.data == 'create_new_avatar')
async def create_avatar(
    call: CallbackQuery, state: FSMContext, texts: Texts
):
    await chain_messages[-1].send(
        chat_id=call.message.chat.id,
        state=state,
        texts=texts
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
        reply_markup = keyboards.input_simple_avatar_name(texts)
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
    file_id = await state.get_value('nano_avatar_id')
    avatar_name = m.text.strip()
    await state.clear()

    can_create_avatar = await UsersRepo(db).get_one_field('can_create_avatar', id=m.from_user.id)
    if not can_create_avatar:
        await m.answer(
            texts.payment.buy_avatar(payments_service.model_level_0_price),
            reply_markup=await get_buy_new_avatar_kb(user_id=m.from_user.id, texts=texts)
        )
        return

    wait_msg = await m.answer(texts.avatar.WAIT_MSG_CREATE_AVATAR)
    await avatars_service.add_simple_avatar(
        user_id=m.from_user.id,
        file_id=file_id,
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


@router.callback_query(keyboards.callback_datas.InputMyNameForAvatarCallback.filter())
@db_connect()
async def input_my_name_for_avatar(
    call: CallbackQuery, state: FSMContext,
    db: AsyncSession, texts: Texts
):
    file_id = await state.get_value('nano_avatar_id')
    avatar_name = call.from_user.full_name

    can_create_avatar = await UsersRepo(db).get_one_field('can_create_avatar', id=call.from_user.id)
    if not can_create_avatar:
        await buy_new_avatar(call, texts)
        return

    wait_msg = await call.message.answer(texts.avatar.WAIT_MSG_CREATE_AVATAR)
    await avatars_service.add_simple_avatar(
        user_id=call.from_user.id,
        file_id=file_id,
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
            texts=texts, avatar_id=avatar.id, models=avatar.models
        )
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
            'Вы отправили только {} фото вместо 10. Пожалуйста, отправьте 10 фото'
            .format(count_photos)
        )
        return

    model_id = await state.get_value('model_id')
    if not model_id:
        model_id = await ModelsRepo(db).get_one_field(
            field='id',
            user_id=m.from_user.id,
            status='paid',
            diffusers_url=None
        )

    if not model_id:
        raise Exception('Не найден model_id для юзера {}'.format(m.from_user.id))

    await avatars_service.create_modeling_model(
        user_id=m.from_user.id,
        file_ids=list(map(lambda x: x.photo[-1].file_id, media_group)),
        model_id=model_id,
        db=db
    )

    await m.answer(texts.avatar.WAIT_MSG_CREATE_AVATAR_PRO)


async def get_buy_new_avatar_kb(
    user_id: int, texts: Texts
):
    price_simple = payments_service.model_level_0_price
    pay_data_simple = await payment_factory.create_payment(
        amount=price_simple,
        description='Покупка Simple аватара',
        payment_method='yookassa',
        metadata=dict(
            user_id=user_id,
            model_level=1,
            type='avatar'
        )
    )
    return keyboards.pay_url_kb(
        pay_url=pay_data_simple.url, texts=texts
    )


@router.callback_query(F.data == 'buy_new_avatar')
async def buy_new_avatar(
    call: CallbackQuery, texts: Texts
):
    await call.message.answer(
        texts.payment.buy_avatar(payments_service.model_level_0_price),
        reply_markup=await get_buy_new_avatar_kb(user_id=call.from_user.id, texts=texts)
    )
