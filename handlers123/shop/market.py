from pymongo import MongoClient
from aiogram import types

database = MongoClient(
    "mongodb+srv://maksemqwerty:maksem228@cluster0.mylnsur.mongodb.net/?retryWrites=true&w=majority").res

marketplace_collection = database['marketplace']



marketplace_collection.insert_one({'id':1234})



class Marketplase:
    def __init__():
        ...
        
    async def sale_oil(callback: types.CallbackQuery) -> None:
        ...

    async def sale_food(callback: types.CallbackQuery) -> None:
        ...

    async def sale_car(callback: types.CallbackQuery) -> None:
        ...

    async def buy_oil(callback: types.CallbackQuery) -> None:
        ...

    async def buy_food(callback: types.CallbackQuery) -> None:
        ...

    async def buy_car(callback: types.CallbackQuery) -> None:
        ...

    async def oil_list() -> list:
        ...

    async def food_list() -> list:
        ...

    async def cars_list() -> list:
        ...