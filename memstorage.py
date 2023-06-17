from aiogram.dispatcher.filters.state import StatesGroup, State


class Registration(StatesGroup):
    begin = State()
    name = State()
    courier = State()
