from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


def Registration():
    start = KeyboardButton('Регистрация')
    menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    menu.add(start)
    return menu


def IsCourierButtons():
    yes = KeyboardButton("Да")
    no = KeyboardButton("Нет")
    menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    menu.add(yes, no)
    return menu


def MenuButtons():
    menu = ReplyKeyboardMarkup(resize_keyboard=True)
    settings_button = KeyboardButton("Настройки")
    create_delivery = KeyboardButton("Создать доставку")
    menu.add(create_delivery, settings_button)
    return menu

def SettingsInlineButtons():
    choice = InlineKeyboardMarkup()
    change_name_button = InlineKeyboardButton("Имя", callback_data="change_name")
    change_courier_button = InlineKeyboardButton("Курьерство", callback_data="change_courier")
    choice.add(change_courier_button, change_name_button)
    
