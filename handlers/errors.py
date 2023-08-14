from aiogram import Router
import traceback
from data.config import *


router = Router()


@router.error()
async def error_handler(event, bot):
    text = f"⚠️ <b>Возникла непредвиденная ошибка</b>:\n\n  {event.exception}"
    await bot.send_message(ADMINS[0], text)

    text = traceback.format_exc().split('\n')
    text = [f"<u>{text[0]}</u>"] + \
           list(map(lambda x: f"<i>{x}</i>" if x.strip()[:4] == 'File' else f"<b> -> {x}</b>", text[1:-2])) + \
           [f"<b>{text[-2]}</b>"]
    await bot.send_message(ADMINS[0], '\n\n'.join(text))

