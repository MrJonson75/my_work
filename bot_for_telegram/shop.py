

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import sqlite3

api = "ывапывапывапывапывапывапывапывапы"
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

start_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Рассчитать'),
         KeyboardButton(text='Информация')],
        [KeyboardButton(text='Купить')]
    ], resize_keyboard=True
)

inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton('Рассчитать норму калорий ', callback_data='calories'),
         InlineKeyboardButton('Формулы расчёта', callback_data='formulas')]
    ]
)

catalog_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton('Продукт 1',
                              callback_data="product_buying"),
         InlineKeyboardButton('Продукт 2',
                              callback_data="product_buying"),
         InlineKeyboardButton('Продукт 3',
                              callback_data="product_buying"),
         InlineKeyboardButton('Продукт 4',
                              callback_data="product_buying")]
    ]
)


class UserState(StatesGroup):
    weight = State()
    growth = State()
    age = State()


@dp.message_handler(commands=['start'])
async def start(message):
    with open('images/logo.jpg', "rb") as img:
        await message.answer_photo(img, f'Уважаемый(ая) {message.from_user.username}, '
                                        f'добро пожаловать в магазин Витамины для всех!', reply_markup=start_menu)


@dp.message_handler(text='Рассчитать')
async def get_calories(message):
    await message.answer('Выберите опцию:', reply_markup=inline_kb)


@dp.message_handler(text='Информация')
async def get_info(message):
    with open('images/intro.png', "rb") as img:
        await message.answer_photo(img,
                                   'онлайн-магазин по продаже нутрицевтиков и натуральных экологичных '
                                   'товаров для здоровья, молодости и красоты.'
                                   )


@dp.message_handler(text='Купить')
async def get_buying_list(message):
    connection = sqlite3.connect('catalog_of_goods.db')
    cursor = connection.cursor()
    cursor.execute(" SELECT part_number, description, price FROM Catalog")
    items = cursor.fetchall()
    connection.commit()
    connection.close()
    for item in items:
        await message.answer(f'Название: Продукт {item[0]} | Описание: {item[1]} | Цена: {item[2]}')
        with open(f'images/{item[0]}.png', "rb") as prod1:
            await message.answer_photo(prod1)
    await message.answer('Выберите продукт для покупки:', reply_markup=catalog_kb)


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5')
    await call.answer()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()
    await call.answer()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    calories = (10 * int(data["weight"])) + (6.25 * int(data["growth"])) - (5 * int(data["age"])) + 5
    await message.answer(f"Калорий для оптимального похудения {calories}")
    await state.finish()


@dp.message_handler()
async def all_message(message):
    await message.answer('Введите команду /start, чтобы начать.')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
