from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def Registration():
    start = KeyboardButton('Начать заполнять профиль')
    menu = ReplyKeyboardMarkup(resize_keyboard=True)
    menu.add(start)
    return menu
