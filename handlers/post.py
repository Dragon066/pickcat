from aiogram import Router, F
import datetime as dt

from database import db, process_text
from middlewares import CheckAdminMiddleware
from states import EditStates
from keyboards import kb_edit_post, EditPostCallbackFactory

router = Router()
router.message.middleware(CheckAdminMiddleware())


@router.message(~F.via_bot, F.photo, flags={'admin': True})
async def post_new_photo(msg):
    msgphoto = msg.photo[-1]

    query = '''INSERT INTO cats_info (file_id, author_id, author_username, text, file_unique_id, 
    update_author_id, update_author_username)
    VALUES(%s, %s, %s, %s, %s, %s, %s)'''

    uniq = msgphoto.file_unique_id
    photo = msgphoto.file_id
    id = msg.from_user.id
    username = msg.from_user.username
    text = process_text(msg.caption) if msg.caption else ''

    vars = [photo, id, username, text, uniq, id, username]
    db.post(query, vars)

    res = db.select('''SELECT * FROM cats_info WHERE file_id = %s''', [photo])[-1]
    message = f'👍 Фото успешно добавлено' \
              f'\n<b>ID</b>: {res["id"]}' \
              f'\n<b>Текст</b>: <code>{res["text"]}</code>'

    await msg.reply(message, reply_markup=kb_edit_post(res["id"]))


@router.callback_query(EditPostCallbackFactory.filter(), flags={'admin': True})
async def callback_post(call, callback_data, state, bot):
    id = callback_data.id
    if callback_data.action == 'edit':
        photo = db.select('SELECT file_id FROM cats_info WHERE id = %s', [id])[0]['file_id']
        await call.message.reply_photo(photo=photo, caption=f'✏️ Редактируем запись #<b>{id}</b>, введите новый текст:'
                                                            f'\n<i>(/cancel для отмены)</i>')
        await state.update_data(id=id)
        await state.set_state(EditStates.text)
    if callback_data.action == 'delete':
        query = '''DELETE FROM cats_info WHERE id = %s'''
        db.post(query, [id])
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'❌ Запись #<b>{id}</b> удалена')
    await call.answer()


@router.message(EditStates.text, flags={'admin': True})
async def set_new_text(msg, state):
    text = process_text(msg.text)
    data = await state.get_data()
    id = data['id']
    author_id = msg.from_user.id
    author_username = msg.from_user.username
    date = dt.datetime.now()
    await state.clear()
    db.post('''UPDATE cats_info SET text = %s, update_author_id = %s, update_author_username = %s,
     update_date = %s WHERE id = %s''', (text, author_id, author_username, date, id))
    await msg.reply(f"✏️ Для записи <b>#{id}</b> применён новый контекст:\n<code>{text}</code>")


@router.message(F.via_bot, F.via_bot.id == 6246978074, F.photo, flags={'admin': True})
async def get_photo(msg):
    photo = msg.photo[-1].file_unique_id
    query = '''SELECT * FROM cats_info WHERE file_unique_id = %s'''

    res = db.select(query, [photo])[-1]
    message = f'''🔎 Информация по фото:
<b>ID</b>: <code>{res["id"]}</code>
<b>Текст</b>: <code>{res["text"]}</code>
<b>Автор</b>: @{res["author_username"]}
<b>Добавлено</b>: <code>{res["date"].strftime("%H:%M, %d %B %Y")}</code>
'''
    if res["update_date"] != res["date"]:
        message += f'''<b>Изменено</b>: @{res["update_author_username"]}
<b>Дата изменения</b>: <code>{res["update_date"].strftime("%H:%M, %d %B %Y")}</code>
'''

    await msg.reply(message, reply_markup=kb_edit_post(res["id"]))

