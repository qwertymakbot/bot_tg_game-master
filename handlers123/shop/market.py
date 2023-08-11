from pymongo import MongoClient
from aiogram import types, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage 
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext 
from bot import dp

database_res = MongoClient(
    "mongodb+srv://maksemqwerty:maksem228@cluster0.mylnsur.mongodb.net/?retryWrites=true&w=majority").res

database = MongoClient(
    "mongodb+srv://maksemqwerty:maksem228@cluster0.mylnsur.mongodb.net/?retryWrites=true&w=majority").data


marketplace_collection = database_res['marketplace']


class MarketplaceStates(StatesGroup):

    price = State()
    quantity = State()




class Marketplace:
    def __init__(self):
        ...

    async def sale_oil(self, callback: types.CallbackQuery, price, quantity) -> str:
        marketplace_collection.insert_one({
            'id': callback.from_user.id,
            'product': 'oil',
            'price': price,
            'volume': quantity
        })
        return 'Обьявление успешно добавлено'

    async def sale_food(self, callback: types.CallbackQuery, price, quantity) -> str:
        marketplace_collection.insert_one({
            'id': callback.from_user.id,
            'product': 'food',
            'price': price,
            'volume': quantity
        })
        return 'Обьявление успешно добавлено'


    async def sale_car(self, callback: types.CallbackQuery, price, quantity, name_car) -> str:
        marketplace_collection.insert_one({
            'id': callback.from_user.id,
            'product': 'car',
            'name_car': name_car,
            'price': price,
            'volume': quantity
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


async def market_sale_food(message: types.Message, callback: types.CallbackQuery, state: MarketplaceStates.quantity):
    user_info = database.users.find_one({'id': callback.from_user.id})
    user_food = int(user_info['food'])
    data_food = message.text
    if user_food >= data_food:
        await callback.message.answer('Укажите количество еды в кг')
        await MarketplaceStates.next()
    else:
        await callback.message.answer('Ты что-то сделал не так')
        await MarketplaceStates.finish()
    
    

def register_handlers_market(dp: Dispatcher):
    dp.register_message_handler(market_sale_food, content_types=['text'], state=MarketplaceStates.quantity)