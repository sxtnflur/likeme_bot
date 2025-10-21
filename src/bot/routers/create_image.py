from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from bot import keyboards
from bot.middlewares.media_group import MediaMiddleware
from database import db_connect, UsersRepo, AvatarsRepo
from depends import image_generator_service
from schemas.avatars import AvatarSchema
from sqlalchemy.ext.asyncio import AsyncSession
from texts.base import get_main_menu_button, Texts
from bot.states.create_image import CreateImageStates

router = Router()
router.message.middleware(MediaMiddleware(latency=1))


@router.message(F.text.in_(get_main_menu_button('CREATE_IMAGE')))
async def create_image(
    m: Message, state: FSMContext, texts: Texts
):
    await m.answer(texts.generation.START_CREATE_IMAGE)
    await state.set_state(CreateImageStates.send_prompt)


@router.callback_query(F.data == 'create_image')
async def create_image_call(
    call: CallbackQuery, state: FSMContext, texts: Texts
):
    await call.message.edit_text(texts.generation.START_CREATE_IMAGE)
    await state.set_state(CreateImageStates.send_prompt)


@router.message(CreateImageStates.send_prompt)
@db_connect()
async def get_prompt(
    m: Message,
    state: FSMContext,
    texts: Texts,
    db: AsyncSession,
    media_group: list[Message] = None
):
    get_file_id = lambda x: x.photo[-1].file_id

    if m.media_group_id:
        file_ids = list(map(get_file_id, media_group))
        await state.update_data(create_image_file_ids=file_ids)
        prompt = await state.get_value('create_image_prompt')
    elif m.photo:
        file_ids = [get_file_id(m)]
        await state.update_data(create_image_file_ids=file_ids)
        prompt = await state.get_value('create_image_prompt')
    elif m.text:
        prompt = m.text.strip()
        await state.update_data(create_image_prompt=prompt)
        file_ids = await state.get_value('create_image_file_ids')
    else:
        return

    chosen_avatar = await state.get_value('create_image_chosen_avatar')
    if not chosen_avatar:
        chosen_avatar = await AvatarsRepo(db).get_by_user_current(user_id=m.from_user.id)
        chosen_avatar = AvatarSchema.model_validate(chosen_avatar)
        await state.update_data(create_image_chosen_avatar=chosen_avatar)

    await m.answer(
        texts.generation.pre_create_image(prompt=prompt,
                               has_images=bool(file_ids),
                               chosen_avatar_name=chosen_avatar.name),
        reply_markup=keyboards.pre_generate_image(
            has_prompt=bool(prompt), has_images=bool(file_ids),
            chosen_avatar=chosen_avatar,
            texts=texts
        )
    )


@router.callback_query(keyboards.callback_datas.SelectIsPrivateCallback.filter())
async def select_is_private(call: CallbackQuery, texts: Texts):
    new_ikb = []
    for row in call.message.reply_markup.inline_keyboard:
        new_row = []
        for btn in row:
            callback_data = keyboards.callback_datas.SelectIsPrivateCallback.from_callback_data(btn.callback_data)
            if callback_data:
                is_private = not callback_data.is_private
                btn.callback_data = keyboards.callback_datas.SelectIsPrivateCallback(is_private=is_private).pack()
                btn.text = texts.generation.is_private_button(is_private)
            new_row.append(btn)
        new_ikb.append(new_row)

    await call.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=new_ikb))


@router.callback_query(keyboards.callback_datas.StartImageGenCallback.filter())
@db_connect()
async def start_gen(
    call: CallbackQuery,
    state: FSMContext,
    texts: Texts,
    db: AsyncSession
):
    data = await state.get_data()
    await state.clear()
    prompt = data.get('create_image_prompt')
    file_ids = data.get('create_image_file_ids', [])

    is_private = None
    for row in call.message.reply_markup.inline_keyboard:
        for btn in row:
            callback_data = keyboards.callback_datas.SelectIsPrivateCallback.from_callback_data(btn.callback_data)
            if callback_data:
                is_private = callback_data.is_private
    if is_private is None:
        raise Exception('Не найден is_private')

    await image_generator_service.generate_image(
        message=call.message,
        user_id=call.from_user.id,
        prompt=prompt,
        db=db,
        texts=texts,
        prompt_image_file_ids=file_ids,
        is_private=is_private,
        session=call.bot.session._session
    )