from pymongo import MongoClient
from aiogram import types

database = MongoClient(
    "mongodb+srv://maksemqwerty:maksem228@cluster0.mylnsur.mongodb.net/?retryWrites=true&w=majority").res

marketplace_collection = database['marketplace']


class Marketplace:
    def __init__(self):
        ...

    async def sale_oil(self, callback: types.CallbackQuery, price, volume) -> str:
        marketplace_collection.insert_one({
            'id': callback.from_user.id,
            'product': 'oil',
            'price': price,
            'volume': volume
        })
        return 'Обьявление успешно добавлено'

    async def sale_food(self, callback: types.CallbackQuery, price, volume) -> str:
        marketplace_collection.insert_one({
            'id': callback.from_user.id,
            'product': 'food',
            'price': price,
            'volume': volume
        })
        return 'Обьявление успешно добавлено'


    async def sale_car(self, callback: types.CallbackQuery, price, volume, name_car) -> str:
        marketplace_collection.insert_one({
            'id': callback.from_user.id,
            'product': 'car',
            'name_car': name_car,
            'price': price,
            'volume': volume
        })
        return 'Обьявление успешно добавлено'


    async def buy_oil(self, callback: types.CallbackQuery) -> None:
        ...

        async def buy_food(self, callback: types.CallbackQuery) -> None:
            ...

        async def buy_car(self, callback: types.CallbackQuery) -> None:
            ...

        async def oil_list(self) -> list:
            return marketplace_collection.find({'product': 'oil'})

        async def food_list(self) -> list:
            return marketplace_collection.find({'product': 'food'})

        async def cars_list(self) -> list:
            return marketplace_collection.find({'product': 'car'})
