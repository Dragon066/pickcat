from aiogram import Router
from aiogram.filters import Command


router = Router()


@router.message(Command('cancel'))
async def cancel_handler(msg, state):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await msg.reply('❌ Отменено')
