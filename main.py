from aiogram.dispatcher import FSMContext
from dotenv import dotenv_values
import logging
from aiogram import Bot, Dispatcher, executor, types
from database import DataBase
import memstorage
import markups
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()

config = dotenv_values(".env")

API_TOKEN = config["token"]

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot=bot, storage=MemoryStorage())

data = DataBase(config["dbname"], config["login"], config["password"], config["postgres"], config["port"])


def in_data_base(id) -> bool:
    return data.check_chat_id(id) != []


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    check = in_data_base(message.from_user.id)
    if not check:
        data.insert_into_client_chat_id(message.from_user.id)
        await message.answer("Здравствуйте, вас приветствует бот по работе с курьерами.",
                             reply_markup=markups.Registration())
        await memstorage.Registration.begin.set()


@dp.message_handler(state=memstorage.Registration.begin)
async def start_registration(message: types.Message):
    await message.answer("Напишите ваше имя:")
    await memstorage.Registration.name.set()


@dp.message_handler(state=memstorage.Registration.name)
async def reg_name(message: types.Message, state: FSMContext):
    name = message.text.title()
    data.insert_into_client_name(message.from_user.id, name)
    await message.answer("Вы являетесь курьером?", reply_markup=markups.IsCourierButtons())
    await memstorage.Registration.courier.set()


async def end_registration(message, state):
    await message.answer("Регистрация завершена.", reply_markup=markups.MenuButtons())
    await state.finish()


@dp.message_handler(state=memstorage.Registration.courier)
async def add_is_courier(message: types.Message, state: FSMContext):
    match message.text.lower():
        case "да":
            data.insert_into_client_courier(message.from_user.id, True)
            await end_registration(message, state)
        case "нет":
            data.insert_into_client_courier(message.from_user.id, False)
            await end_registration(message, state)
        case _:
            await message.reply("Неверное значение.")


@dp.message_handler()
async def menu_check(message: types.Message):
    text = message.text
    match text:
        case "Настройки":
            await message.answer("Что вы хотите изменить?", reply_markup=markups.SettingsInlineButtons())
            await memstorage.Changing.begin.set()
        case "Создать доставку":
            pass
        case _:
            await message.answer("Неизвестная команда")


@dp.message_handler(state=memstorage.Changing.changeName)
async def change_name(message: types.Message, state: FSMContext):
    name = message.text.title()
    data.insert_into_client_name(message.from_user.id, name)
    await message.answer(f"Ваше имя изменено на {name}.")
    await state.finish()


@dp.message_handler(state=memstorage.Changing.changeCourier)
async def changeCourier(message: types.Message, state: FSMContext):
    match message.text.lower():
        case "да":
            data.insert_into_client_courier(message.from_user.id, True)
            await message.answer("Ваши данные изменены")
            await state.finish()
        case "нет":
            data.insert_into_client_courier(message.from_user.id, False)
            await message.answer("Ваши данные изменены")
            await state.finish()
        case _:
            await message.reply("Неверное значение.")


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("change_"), state=memstorage.Changing.begin)
async def changing(callback: types.CallbackQuery):
    param = callback.data.split("_")[1]
    match param:
        case "name":
            await bot.send_message(callback.from_user.id, "Введите новое имя:")
            await memstorage.Changing.changeName.set()
        case "courier":
            await bot.send_message(callback.from_user.id, "Вы хотите быть курьером?",
                                   reply_markup=markups.IsCourierButtons())
            await memstorage.Changing.changeCourier.set()
        case _:
            print("что-то пошло не так")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
