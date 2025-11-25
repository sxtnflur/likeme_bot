from aiogram import Bot
from aiogram.fsm.context import FSMContext

key = 'del-msgs'


async def save_msgs_to_delete(state: FSMContext, msg_id: int | list[int]):
    del_msgs: list[int] = await state.get_value(key, [])
    if isinstance(msg_id, int):
        del_msgs.append(msg_id)
    elif isinstance(msg_id, list):
        del_msgs.extend(msg_id)
    await state.update_data(**{key: del_msgs})


async def delete_saved_msgs(state: FSMContext, bot: Bot, chat_id: int):
    del_msgs: list[int] = await state.get_value(key)
    if not del_msgs:
        return
    await bot.delete_messages(chat_id, message_ids=del_msgs)