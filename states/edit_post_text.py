from aiogram.fsm.state import State, StatesGroup


class EditStates(StatesGroup):
    text = State()
