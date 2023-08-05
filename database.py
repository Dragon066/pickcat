from data.config import *
import psycopg2
from psycopg2.extras import RealDictCursor


class Database():
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, host, port, database, user, password):
        self.connection = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )

        self.connection.autocommit = True

        self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)

    def select(self, query, vars=tuple()):
        self.cursor.execute(query, vars)
        res = self.cursor.fetchall()
        return res

    def post(self, query, vars=tuple()):
        self.cursor.execute(query, vars)

    def close(self):
        self.cursor.close()
        self.connection.close()
        delattr(Database, 'instance')

    def reconnect(self):
        self.__init__(HOST, PORT, DATABASE, USER, PASSWORD)


db = Database(HOST, PORT, DATABASE, USER, PASSWORD)


def process_text(text):
    text = text.replace('ё', 'е').replace('Ё', 'Е')

    text = text.lower().strip()

    return text
