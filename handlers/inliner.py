from aiogram import types, Router
from aiogram import html

from random import shuffle

from database import db, process_text
from data.config import *

router = Router()


@router.inline_query()
async def inline_mode(inline_query):
    text = inline_query.query
    caption = None

    if '/' in text:
        caption = html.quote(text[text.find('/') + 1:].strip())
        text = text[:text.find('/')].strip()

    text = process_text(text)

    offset = int(inline_query.offset) if inline_query.offset else 0

    if len(text) > 0:
        query = '''
        SELECT id, file_id, text, word_similarity(%s, text) as ratio
        FROM cats_info ci 
        WHERE word_similarity(%s, text) > %s
        ORDER BY ratio DESC, date DESC
        OFFSET %s LIMIT %s
        '''

        res = db.select(query, [text, text, SIMILARITY, offset, LIMIT])
    else:
        query = '''
        SELECT id, file_id
        FROM cats_info ci
        ORDER BY date DESC
        OFFSET %s LIMIT %s
        '''

        res = db.select(query, [offset, LIMIT])

    results = [types.InlineQueryResultCachedPhoto(id=str(photo['id']), photo_file_id=photo['file_id'],
                                                  caption=caption) for photo in res]

    if len(text) == 0:
        shuffle(results)

    nxt_offset = "" if len(res) < LIMIT else str(offset + LIMIT)

    await inline_query.answer(results, cache_time=CACHE_TIME, next_offset=nxt_offset)
