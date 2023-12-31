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


async def delete_delivery(message, state):
    await state.finish()
    await message.answer("Создание доставки отменено.")
    data.delete_delivery(message.from_user.id)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("delivery_"))
async def delivery(callback: types.CallbackQuery):
    call = callback.data.split("_")
    if call[1] == "cancel":
        await bot.send_message(callback.from_user.id, "Доставка отклонена.")
    else:
        delivery_id = call[2]
        info = data.get_delivery_info(delivery_id)
        if info[2] is None:
            data.add_courier_to_delivery(delivery_id, callback.from_user.id)
            await bot.send_message(callback.from_user.id, "Доставка принята.")
            user_id = info[1]
            await bot.send_message(callback.from_user.id, "Информация по заказу: \n" + info[-1])
            await bot.send_message(user_id, f"Пользователь {callback.from_user.url} принял доставку.")
        else:
            await bot.send_message(callback.from_user.id, "Доставку уже приняли.")


async def message_for_courier(message, delivery_info, courier):
    await bot.send_message(courier[0], f"Была создана доставка:",
                           reply_markup=markups.AcceptDelivery(delivery_info[0]))
    location_to = delivery_info[3].split("_")
    await bot.send_location(courier[0], location_to[0], location_to[1])
    location_from = delivery_info[4].split("_")
    await bot.send_message(courier[0], "До:")
    await bot.send_location(courier[0], location_from[0], location_from[1])


@dp.message_handler(state=memstorage.MakeDelivery.deliveryDescription)
async def set_delivery_description(message: types.Message, state: FSMContext):
    if message.text.lower() != "отменить":
        text = message.text
        delivery_id = data.get_delivery_id(message.from_user.id)
        data.add_description(delivery_id, text)
        await message.answer("Доставка создана, когда курьер его примет, вам придет уведомление.",
                             reply_markup=markups.MenuButtons())
        couriers = data.get_couriers_chat_id()
        delivery_info = data.get_delivery_info(delivery_id)
        print(couriers)
        for courier in couriers:
            if courier[0] != message.from_user.id:
                await message_for_courier(message, delivery_info, courier)
        await state.finish()
    else:
        await delete_delivery(message, state)


@dp.message_handler(state=memstorage.MakeDelivery.deliveryTo, content_types=['location', "text"])
async def set_location_to(message: types.Message, state: FSMContext):
    if message.content_type != "text":
        delivery_id = data.get_delivery_id(message.from_user.id)
        data.add_location_to(delivery_id, message.location.latitude, message.location.longitude)
        await message.answer(
            "Введите описание заказа: что забрать, картинки к заказу, и так далее (В одном сообщении).")
        await memstorage.MakeDelivery.deliveryDescription.set()
    else:
        if message.text.lower() == "отменить":
            await delete_delivery(message, state)


@dp.message_handler(state=memstorage.MakeDelivery.deliveryFrom, content_types=['location', "text"])
async def set_location_from(message: types.Message, state: FSMContext):
    if message.content_type != "text":
        data.add_location_from(message.from_user.id, message.location.latitude, message.location.longitude)
        await message.answer("Отправьте геолокацию, куда нужно доставить заказ.")
        await memstorage.MakeDelivery.deliveryTo.set()
    else:
        if message.text.lower() == "отменить":
            await state.finish()
            await message.answer("Создание доставки отменено.", reply_markup=markups.MenuButtons())


@dp.message_handler()
async def menu_check(message: types.Message):
    text = message.text
    match text:
        case "Настройки":
            await message.answer("Что вы хотите изменить?", reply_markup=markups.SettingsInlineButtons())
            await memstorage.Changing.begin.set()
        case "Создать доставку":
            await message.answer("Отправьте геолокацию, откуда необходимо доставить товар.",
                                 reply_markup=markups.Cancel())
            await memstorage.MakeDelivery.deliveryFrom.set()
        case _:
            await message.answer("Неизвестная команда")


@dp.message_handler(state=memstorage.Changing.changeName)
async def change_name(message: types.Message, state: FSMContext):
    name = message.text.title()
    data.insert_into_client_name(message.from_user.id, name)
    await message.answer(f"Ваше имя изменено на {name}.")
    await state.finish()


@dp.message_handler(state=memstorage.Changing.changeCourier)
async def change_courier(message: types.Message, state: FSMContext):
    match message.text.lower():
        case "да":
            data.insert_into_client_courier(message.from_user.id, True)
            await message.answer("Ваши данные изменены")
        case "нет":
            data.insert_into_client_courier(message.from_user.id, False)
            await message.answer("Ваши данные изменены")
    await state.finish()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("change_"), state=memstorage.Changing.begin)
async def changing(callback: types.CallbackQuery, state: FSMContext):
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
            await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
            await state.finish()


# TODO сделать рассылку курьерам, с возможностью принять заказ после его создания
# TODO сделать обратную связь, что заказ с такими то координатами приняли, прислать пользователя заказчику и чтобы он начал общение с ним для удобства

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
