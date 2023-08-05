from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class EditPostCallbackFactory(CallbackData, prefix='post'):
    action: str
    id: int


def kb_edit_post(id):
    builder = InlineKeyboardBuilder()
    builder.button(text='✏️ Редактировать', callback_data=EditPostCallbackFactory(action='edit', id=id))
    builder.button(text='❌ Удалить', callback_data=EditPostCallbackFactory(action='delete', id=id))
    return builder.as_markup()
