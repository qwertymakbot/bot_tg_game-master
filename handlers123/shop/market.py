from pymongo import MongoClient
from aiogram import types, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from create_bot import dp
import random
from bot import username, bot

database_res = MongoClient(
    "mongodb+srv://maksemqwerty:maksem228@cluster0.mylnsur.mongodb.net/?retryWrites=true&w=majority").res

database = MongoClient(
    "mongodb+srv://maksemqwerty:maksem228@cluster0.mylnsur.mongodb.net/?retryWrites=true&w=majority").data

marketplace_collection = database_res['marketplace']


class MarketplaceStatesSaleFood(StatesGroup):
    price = State()
    quantity = State()


class MarketplaceStatesSaleOil(StatesGroup):
    price = State()
    quantity = State()


class MarketplaceStatesSaleCar(StatesGroup):

    car_name = State()
    price = State()

class Marketplace:
    def __init__(self):
        ...




    async def sale_oil(data: dict) -> str:
        marketplace_collection.insert_one({
            '_id': random.randint(0,10000000),
            'id': data['id'],
            'product': 'oil',
            'price': data['price'],
            'quantity': data['quantity']
        })
        user = database.users.find_one({'id': data['id']})
        database.users.update_one({'id': data['id']}, {'$set': {'oil': int(user['oil']) - int(data['quantity'])}})
        return 'Обьявление успешно добавлено'

    async def sale_food(data: dict) -> str:
        marketplace_collection.insert_one({
            '_id': random.randint(0,10000000),
            'id': data['id'],
            'product': 'food',
            'price': data['price'],
            'quantity': data['quantity']
        })
        user = database.users.find_one({'id': data['id']})
        database.users.update_one({'id': data['id']}, {'$set': {'food': int(user['food']) - int(data['quantity'])}})

    async def sale_car(message: types.Message, price, quantity, name_car) -> str:
        marketplace_collection.insert_one({
            'id': message.from_user.id,
            'product': 'car',
            'name_car': name_car,
            'price': price,
            'quantity': quantity
        })
        return 'Обьявление успешно добавлено'

    async def buy_oil(self, callback: types.CallbackQuery) -> None:
        ...

    async def buy_food(self, callback: types.CallbackQuery) -> None:
        ...

    async def buy_car(self, callback: types.CallbackQuery) -> None:
        ...

    async def oil_list(self) -> list:
        return list(marketplace_collection.find({'product': 'oil'}))

    async def food_list(self) -> list:
        return list(marketplace_collection.find({'product': 'food'}))

    async def cars_list(self) -> list:
        return list(marketplace_collection.find({'product': 'car'}))


@dp.callback_query_handler(text='marketseller_sale_food', state=None)
async def start_sale_food(callback: types.CallbackQuery):
    adds = list(database_res.marketplace.find({'$and': [{'id': callback.from_user.id}, {'product': 'food'}]}))
    if not adds:
        user_info = database.users.find_one({'id': callback.from_user.id})
        user_food = int(user_info['food'])

        await callback.message.answer(f'{await username(callback)}, укажите количество еды (доступно: {user_food} кг)', parse_mode='HTML')
        await MarketplaceStatesSaleFood.quantity.set()
    else:
        await callback.message.edit_text(f'{await username(callback)}, чтобы добавить объявление - удалите объявление с продуктом Еда из категории Мои объявления', parse_mode='HTML')


@dp.message_handler(content_types=['text'], state=MarketplaceStatesSaleFood.quantity)
async def market_sale_food(message: types.Message, state: FSMContext):
    if int(message.text) <= 0:
        await message.answer(f'{await username(message)}, введите корректное количество!', parse_mode='HTML')
        return
    user_info = database.users.find_one({'id': message.from_user.id})
    user_food = int(user_info['food'])
    try:
        data_food = int(message.text)
        if user_food >= data_food:
            await message.answer(f'{await username(message)}, укажите цену за данное количество:', parse_mode='HTML')
            await MarketplaceStatesSaleFood.price.set()
            async with state.proxy() as data:
                data['quantity'] = int(message.text)
        else:
            await message.answer(f'{await username(message)}, у вас недостаточно еды!', parse_mode='HTML')
            await state.finish()
    except:
        await message.answer(f'{await username(message)}, вы некорректно ввели количество', parse_mode='HTML')
        await state.finish()


@dp.message_handler(content_types=['text'], state=MarketplaceStatesSaleFood.price)
async def market_sale_food_price(message: types.Message, state: FSMContext):
    if int(message.text) <= 0:
        await message.answer(f'{await username(message)}, введите корректную цену!', parse_mode='HTML')
        return
    try:
        async with state.proxy() as data:
            data['price'] = int(message.text)
            data['id'] = message.from_user.id
            data['product'] = 'food'
            data = await load_data(data)
            await Marketplace.sale_food(data=data)
            await state.finish()
        await message.answer(f'{await username(message)}, ресурсы списаны с вашего счета, деньги поступят на счёт после того как другой пользователь приобретёт ваш товар', parse_mode='HTML')
    except:
        await message.answer(f'{await username(message)}, вы некорректно ввели цену!', parse_mode='HTML')
        await state.finish()


@dp.callback_query_handler(text='marketseller_sale_oil', state=None)
async def start_sale_oil(callback: types.CallbackQuery):
    adds = list(database_res.marketplace.find({'$and': [{'id': callback.from_user.id}, {'product': 'oil'}]}))
    if not adds:
        user_info = database.users.find_one({'id': callback.from_user.id})
        user_oil = int(user_info['oil'])
        await callback.message.edit_text(f'{await username(callback)}, укажите количество топлива (доступно: {user_oil} л)', parse_mode='HTML')
        await MarketplaceStatesSaleOil.quantity.set()
    else:
        await callback.message.edit_text(f'{await username(callback)}, чтобы добавить объявление - удалите объявление с продуктом Топливо из категории Мои объявления', parse_mode='HTML')

@dp.message_handler(content_types=['text'], state=MarketplaceStatesSaleOil.quantity)
async def market_sale_oil(message: types.Message, state: FSMContext):
    if int(message.text) <= 0:
        await message.answer(f'{await username(message)}, введите корректное количество!', parse_mode='HTML')
        return
    user_info = database.users.find_one({'id': message.from_user.id})
    user_oil = int(user_info['oil'])
    try:
        data_oil = int(message.text)
        if user_oil >= data_oil:
            await message.answer(f'{await username(message)}, укажите цену за данное количество:', parse_mode='HTML')
            await MarketplaceStatesSaleOil.price.set()
            async with state.proxy() as data:
                data['quantity'] = int(message.text)
        else:
            await message.answer(f'{await username(message)}, у вас недостаточно топлива!', parse_mode='HTML')
            await state.finish()
    except:
        await message.answer(f'{await username(message)}, вы некорректно ввели количество', parse_mode='HTML')
        await state.finish()

@dp.message_handler(content_types=['text'], state=MarketplaceStatesSaleOil.price)
async def market_sale_oil_price(message: types.Message, state: FSMContext):
    if int(message.text) <= 0:
        await message.answer(f'{await username(message)}, введите корректную цену!', parse_mode='HTML')
        return
    try:
        async with state.proxy() as data:
            data['price'] = int(message.text)
            data['id'] = message.from_user.id
            data['product'] = 'oil'
            d = await load_data(data)
            await Marketplace.sale_oil(data=d)
        await state.finish()
        await message.answer(
            f'{await username(message)}, ресурсы списаны с вашего счета, деньги поступят на счёт после того как другой пользователь приобретёт ваш товар', parse_mode='HTML')
    except:
        await message.answer(f'{await username(message)}, вы некорректно ввели цену!', parse_mode='HTML')
        await state.finish()


async def load_data(data: dict):
    d = {
        'price': data['price'],
        'quantity': data['quantity'],
        'id': data['id'],
        'product': data['product']
    }
    return d
#data = FSMContext.get_data(MarketplaceStatesSaleFood)

# def register_handlers_market(dp: Dispatcher):
# dp.register_callback_query_handler(market_sale_food, text='marketseller_sale_food', state=None)
# dp.register_message_handler(market_sale_food, state=MarketplaceStates.quantity, content_types=['text'])
