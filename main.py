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

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('is_courier'), state=memstorage.Registration.courier)
async def add_is_courier(callback_query: types.CallbackQuery):
    result = (callback_query.data.split("_")[2] == "true")
    print(callback_query.data.split("_")[2])
    # data.insert_into_client_courier(message.from_user.id, result)






if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
