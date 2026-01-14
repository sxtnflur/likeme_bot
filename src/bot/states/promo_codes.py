from aiogram.fsm.state import StatesGroup, State


class PromocodesStates(StatesGroup):
    get_promocode = State()