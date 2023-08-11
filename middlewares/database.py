from aiogram import BaseMiddleware


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, db):
        self.db = db

    async def __call__(self, handler, event, data):
        data['db'] = self.db
        return await handler(event, data)
