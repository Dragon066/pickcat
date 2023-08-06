from aiogram import Router
from aiogram.filters import Command
import datetime as dt

from database import db
from data.config import *
from middlewares.checkadmin import CheckAdminMiddleware

router = Router()
router.message.middleware(CheckAdminMiddleware())


def get_lexem_picture(n):
    if n % 100 in (11, 12, 13, 14) or n % 10 in (0, 5, 6, 7, 8, 9):
        return 'картинок'
    if n % 10 in (1,):
        return 'картинка'
    if n % 10 in (2, 3, 4):
        return 'картинки'


@router.message(Command('help', 'start'))
async def info_text(msg):
    query = '''SELECT count(*) as cnt, max(date) as mx FROM cats_info'''

    res = db.select(query)[0]

    query = '''SELECT count(*) as amount FROM cats_info WHERE now()::date = date::date'''

    res_amount = db.select(query)[0]

    message = f'''<b>🔎 PickCat Bot 🐾</b>
    
🤔 Бот создан для хранения и поиска картинок и мемов с котиками.

Просто наберите в строке набора сообщения: <code>@pickcat_bot текст</code>.
В запросе можно использовать знак <code>/</code> - весь текст после него не будет учтён при поиске, однако прикрепится к картинке.
    
• На данный момент в базе данных <b>{res["cnt"]}</b> {get_lexem_picture(res["cnt"])} 🐈
• Сегодня добавлено <b>{res_amount["amount"]}</b> {get_lexem_picture(res_amount["amount"])}
• Последняя запись осуществлена в <b>{res["mx"].strftime("%H:%M, %d %B %Y")}</b> 📝
• Количество текущих редакторов: <b>{len(ADMINS)}</b> ✏️

Подбор и сортировка картинок осуществляется алгоритмом <b>неточного поиска</b> на основе использования триграмм.

• Время кеширования запроса: <b>{CACHE_TIME} сек.</b> ⏱
• Чёткость неточного поиска: <b>{round(SIMILARITY * 100, 1)}%</b> 🎯

    <i>Developed by @dragon_iva</i> 😼'''

    await msg.answer(message)


@router.message(Command('ping'))
async def ping(msg):
    message = '<b>Pong!</b>\n'
    try:
        start = dt.datetime.now()
        res = db.select('''SELECT 1 as a''')
        if res[0]["a"] == 1:
            message += f'Ответ <code>work</code>: <b>{round((dt.datetime.now() - start).microseconds / 1000)}ms</b>\n'
        else:
            message += f'Ответ <code>work</code>: <b>-</b>\n'

        start = dt.datetime.now()
        res = db.select('''SELECT * FROM cats_info LIMIT 1''')
        if res[0]["id"]:
            message += f'Ответ <code>db_cats</code>: ' \
                       f'<b>{round((dt.datetime.now() - start).microseconds / 1000)}ms</b>\n'
        else:
            message += f'Ответ <code>db_cats</code>: <b>-</b>\n'

        query = '''
        SELECT id, file_id, text, word_similarity(%s, text) as ratio
        FROM cats_info ci 
        WHERE word_similarity(%s, text) > %s
        ORDER BY ratio DESC, date DESC
        OFFSET %s LIMIT %s
        '''
        text = 'кот'
        start = dt.datetime.now()
        res = db.select(query, [text, text, SIMILARITY, 0, LIMIT])
        if len(res) > 0:
            message += f'Ответ <code>inline</code>: <b>{round((dt.datetime.now() - start).microseconds / 1000)}ms</b>'
        else:
            message += f'Ответ <code>inline</code>: <b>-</b>'

        await msg.answer(message)
    except Exception as ex:
        await msg.answer(f'Возникла ошибка <i>{ex}</i>\nПопытка переподключиться к БД...')
        db.reconnect()
        await msg.answer('Создано новое соединение')


@router.message(Command('restart'), flags={'admin': True})
async def restart(msg):
    import os
    import git

    try:
        await msg.answer('♻️ Обновляю файлы...')
        repo = git.Repo()
        current = repo.head.commit
        repo.remotes.origin.pull()
        if current != repo.head.commit:
            list_updates = []

            for commit in repo.iter_commits():
                if commit == current:
                    break
                list_updates.append(commit.message.strip())

            text_updates = '\n• '.join(list_updates)

            text = f'✅ Файлы обновлены\n\n<b>Новые коммиты:</b>\n{text_updates}'
            await msg.answer(text)

    except Exception as ex:
        await msg.answer(f'❌ При обновлении возникла ошибка: <i>{ex}</i>')

    await msg.answer('Перезапуск...')
    os.system('systemctl restart pickcatbot')
