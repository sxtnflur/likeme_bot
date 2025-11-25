from aiogram.fsm.state import StatesGroup, State


class CreateImageStates(StatesGroup):
    send_prompt = State()
    update_prompt = State()