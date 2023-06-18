from aiogram.dispatcher.filters.state import StatesGroup, State


class Registration(StatesGroup):
    begin = State()
    name = State()
    courier = State()


class Changing(StatesGroup):
    begin = State()
    changeName = State()
    changeCourier = State()

