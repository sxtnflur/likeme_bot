from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from bot.keyboards.callback_datas import ScrollingCallback
from texts import Texts
from typing_extensions import Callable, TypeVar

T = TypeVar('T')


def create_list_kb(
        objs: list[T], get_btn: Callable[[T], InlineKeyboardButton], width: int = 2
) -> list[list[InlineKeyboardButton]]:
    """

    :rtype: object
    """
    inl_kb = [[]]
    for obj in objs:
        btn = get_btn(obj)
        if len(inl_kb[-1]) >= width:
            inl_kb.append([btn])
        else:
            inl_kb[-1].append(btn)
    return inl_kb


def create_scrolling_kb(
        page: int,
        limit: int,
        callback_data: type[ScrollingCallback],
        objs: list[T],
        get_btn: Callable[[T], InlineKeyboardButton],
        width: int = 2,
        additional_btns: list[list[InlineKeyboardButton]] | None = None,
        pag_btn_additional_kwargs: dict | None = None,
        pag_left_button: str = '<',
        pag_right_button: str = '>'
) -> InlineKeyboardMarkup:
    inl_kb = create_list_kb(objs, get_btn, width)
    pag_btns = []
    if page > 0:
        if pag_btn_additional_kwargs:
            pag_btns.append(InlineKeyboardButton(
                text=pag_left_button,
                callback_data=callback_data(page=page - 1, limit=limit, **pag_btn_additional_kwargs).pack()
            ))
        else:
            pag_btns.append(InlineKeyboardButton(
                text=pag_left_button, callback_data=callback_data(page=page - 1, limit=limit).pack()
            ))
    if len(objs) == limit:
        if pag_btn_additional_kwargs:
            pag_btns.append(InlineKeyboardButton(
                text=pag_right_button,
                callback_data=callback_data(page=page + 1, limit=limit, **pag_btn_additional_kwargs).pack()
            ))
        else:
            pag_btns.append(InlineKeyboardButton(
                text=pag_right_button, callback_data=callback_data(page=page + 1, limit=limit).pack()
            ))
    if additional_btns:
        inl_kb += additional_btns

    return InlineKeyboardMarkup(inline_keyboard=inl_kb)


#
#
# def create_btn_back(callback_data: str):
#     return InlineKeyboardButton(text=BaseTexts.BACK, callback_data=callback_data)
#
#
# def create_kb_back(callback_data: str):
#     return InlineKeyboardMarkup(inline_keyboard=[[create_btn_back(callback_data)]])


def main_menu(
        texts: Texts
):
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=texts.main_menu_buttons.CREATE_IMAGE)],
        [KeyboardButton(text=texts.main_menu_buttons.AVATAR),
         KeyboardButton(text=texts.main_menu_buttons.PAYMENT)],
        [KeyboardButton(text=texts.main_menu_buttons.FEED),
         KeyboardButton(text=texts.main_menu_buttons.SUPPORT)]
    ],
        resize_keyboard=True)
