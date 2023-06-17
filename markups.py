from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


def Registration():
    start = KeyboardButton('Регистрация')
    menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    menu.add(start)
    return menu


def IsCourierButtons():
    choice = InlineKeyboardMarkup()
    yes_button = InlineKeyboardButton("Да", callback_data="is_courier_true")
    no_button = InlineKeyboardButton("Нет", callback_data="is_courier_false")
    choice.add(yes_button, no_button)
    return choice

