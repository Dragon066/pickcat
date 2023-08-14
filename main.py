import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
import datetime as dt

from data.config import *
from handlers import cancel_state, inliner, commands, post
from database import Database
from middlewares import DatabaseMiddleware


async def on_startup(dispatcher):
    print(f'[{dt.datetime.now().strftime("%d/%b/%y %H:%M:%S")}] Бот запущен за {datetime.now() - STARTUP}')
    db = Database(HOST, PORT, DATABASE, USER, PASSWORD)
    await db.create_pool()
    dispatcher.update.middleware(DatabaseMiddleware(db))


async def on_shutdown(dispatcher):
    print(f'[{dt.datetime.now().strftime("%d/%b/%y %H:%M:%S")}] Бот отключён, время работы: {datetime.now() - STARTUP}')


async def main():
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_routers(cancel_state.router, inliner.router, commands.router, post.router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__""":
    logging.basicConfig(level=logging.WARNING, format='[%(asctime)s] [%(levelname)s]: %(message)s',
                        datefmt='%d/%b/%y %H:%M:%S')
    asyncio.run(main())
