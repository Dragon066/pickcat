from data.config import *
import asyncpg


class Database():
    def __init__(self, host, port, database, user, password):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.pool = None

    async def create_pool(self):
        self.pool = await asyncpg.create_pool(host=self.host,
                                              port=self.port,
                                              database=self.database,
                                              user=self.user,
                                              password=self.password)

    async def select(self, query, vars=tuple()):
        async with self.pool.acquire() as con:
            async with con.transaction():
                result = await con.fetch(query, *vars)
        return result

    async def post(self, query, vars=tuple()):
        async with self.pool.acquire() as con:
            async with con.transaction():
                result = await con.execute(query, *vars)
        return result

    async def close(self):
        self.pool.terminate()

    async def reconnect(self):
        await self.create_pool()


def process_text(text):
    text = text.replace('ё', 'е').replace('Ё', 'Е')

    text = text.lower().strip()

    return text
