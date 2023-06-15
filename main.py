from dotenv import dotenv_values
import logging
from aiogram import Bot, Dispatcher, executor, types
from database import DataBase
import markups

config = dotenv_values(".env")

API_TOKEN = config["token"]

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

data = DataBase(config["dbname"], config["login"], config["password"], config["postgres"], config["port"])


def in_data_base(id) -> bool:
    print(data.check_chat_id(id))
    return data.check_chat_id(id) != []


async def greeting(message):
    await message.reply("Здравствуйте.")


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    if not in_data_base(message.from_user.id):
        await message.answer("Добрый день, начало работы с ботом по работе с курьерами.",
                             reply_markup=markups.Registration())
        data.insert_into_users(message.from_user.id)


@dp.message_handler(commands=['registration'])
async def registration(message: types.Message):
    async def full_name() -> None:
        pass

    async def courier() -> None:
        pass


# @dp.message_handler()
# async def echo(message: types.Message):
#     await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
