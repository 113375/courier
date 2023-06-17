from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def Registration():
    start = KeyboardButton('Регистрация')
    menu = ReplyKeyboardMarkup(resize_keyboard=True)
    menu.add(start)
    return menu


def IsCourierButtons():
    yes = KeyboardButton("Да")
    no = KeyboardButton("Нет")
    menu = ReplyKeyboardMarkup(resize_keyboard=True)
    menu.add(yes, no)
    return menu

