from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag

from data.config import *


class CheckAdminMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        need_admin = get_flag(data, 'admin')
        if not need_admin or data['event_from_user'].id in ADMINS:
            return await handler(event, data)
        await event.reply('Для получения прав редактирования обратитесь к @dragon_iva')
