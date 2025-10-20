from aiogram.fsm.state import StatesGroup, State


class NanobananaAvatarStates(StatesGroup):
    send_photo = State()
    send_name = State()