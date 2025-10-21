from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from bot import keyboards
from bot.middlewares.media_group import MediaMiddleware
from bot.states import NanobananaAvatarStates, CreateModelStates
from database import AvatarsRepo, db_connect, ModelsRepo
from depends import avatars_service
from schemas.avatars import AvatarSchema
from sqlalchemy.ext.asyncio import AsyncSession
from texts.base import Texts, get_main_menu_button

router = Router()
router.message.middleware(MediaMiddleware(1))


@router.message(F.text.in_(get_main_menu_button('AVATAR')))
@db_connect()
async def start_create_image(
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

    await m.answer(
        texts.avatar.AVATARS_LIST,
        reply_markup=keyboards.avatars_list(
            avatars=avatars,
            page=0,
            limit=50
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
    await call.message.edit_text(
        texts.avatar.AVATARS_LIST,
        reply_markup=keyboards.avatars_list(
            avatars=list(map(AvatarSchema.model_validate, avatars)),
            page=callback_data.page,
            limit=callback_data.limit
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
        reply_markup = keyboards.input_simple_avatar_name(texts)
    else:
        reply_markup = None

    await m.delete()
    await m.answer_photo(
        photo=file_id,
        caption=texts.avatar.ON_SEND_AVATAR_PHOTO,
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
    await avatars_service.add_simple_avatar(
        user_id=m.from_user.id,
        file_id=file_id,
        name=avatar_name,
        db=db
    )
    await m.answer(
        texts.avatar.on_create_avatar(avatar_name)
    )


@router.callback_query(keyboards.callback_datas.InputMyNameForAvatarCallback.filter())
@db_connect()
async def input_my_name_for_avatar(
    call: CallbackQuery, state: FSMContext,
    db: AsyncSession, texts: Texts
):
    file_id = await state.get_value('nano_avatar_id')
    avatar_name = call.from_user.full_name
    await avatars_service.add_simple_avatar(
        user_id=call.from_user.id,
        file_id=file_id,
        name=avatar_name,
        db=db
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
    avatar = await AvatarsRepo(db).get_one(id=callback_data.avatar_id)
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
    if len(media_group) < 10:
        await m.answer(
            'Вы отправили только {} фото вместо 10. Пожалуйста, отправьте 10 фото'
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

    await m.answer(
        '<i>Обучение модели началось. Обычно оно занимает 15-30 минут. Пожалуйста подождите...</i>'
    )
