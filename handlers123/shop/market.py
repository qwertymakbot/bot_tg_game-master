from pymongo import MongoClient
from aiogram import types, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from create_bot import dp

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




    async def sale_oil(data) -> str:
        marketplace_collection.insert_one({
            'id': data['id'],
            'product': 'oil',
            'price': data['price'],
            'quantity': data['quantity']
        })
        return 'Обьявление успешно добавлено'

    async def sale_food(data: dict) -> None:
        marketplace_collection.insert_one({
            'id': data['id'],
            'product': 'food',
            'price': data['price'],
            'quantity': data['quantity']
        })
        print('Обьявление успешно добавлено')

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
    user_info = database.users.find_one({'id': callback.from_user.id})
    user_food = int(user_info['food'])
    
    await callback.message.answer(text=f'Укажи количество еды (доступно:{user_food}кг)')
    await MarketplaceStatesSaleFood.quantity.set()


@dp.message_handler(content_types=['text'], state=MarketplaceStatesSaleFood.quantity)
async def market_sale_food(message: types.Message, state: FSMContext):
    user_info = database.users.find_one({'id': message.from_user.id})
    user_food = int(user_info['food'])
    data_food = int(message.text)
    if user_food >= data_food:
        await message.answer('теперь цену')
        await MarketplaceStatesSaleFood.price.set()
        async with state.proxy() as data:
            data['quantity'] = int(message.text)
    else:
        await message.answer('ты что-то сделал не так')
        await state.finish()


@dp.message_handler(content_types=['text'], state=MarketplaceStatesSaleFood.price)
async def market_sale_food_price(message: types.Message, state: FSMContext):
    await message.answer('готово')
    async with state.proxy() as data:
        data['price'] =  int(message.text)
        data['id'] = message.from_user.id
        data=await load_data(data)
        await Marketplace.sale_food(data=data)
        await state.finish()
    print(list(marketplace_collection.find()))


@dp.callback_query_handler(text='marketseller_sale_oil', state=None)
async def start_sale_oil(callback: types.CallbackQuery):
    user_info = database.users.find_one({'id': callback.from_user.id})
    user_oil = int(user_info['oil'])
    await callback.message.answer(text=f'Укажи количество топлива (доступно:{user_oil}л)')
    await MarketplaceStatesSaleOil.quantity.set()


@dp.message_handler(content_types=['text'], state=MarketplaceStatesSaleOil.quantity)
async def market_sale_oil(message: types.Message, state: FSMContext):
    user_info = database.users.find_one({'id': message.from_user.id})
    user_oil = int(user_info['oil'])
    data_oil = int(message.text)
    if user_oil >= data_oil:
        await message.answer('теперь цену')
        await MarketplaceStatesSaleOil.price.set()
        async with state.proxy() as data:
            data['quantity'] = int(message.text)
    else:
        await message.answer('ты что-то сделал не так')
        await state.finish()
    

@dp.message_handler(content_types=['text'], state=MarketplaceStatesSaleOil.price)
async def market_sale_oil_price(message: types.Message, state: FSMContext):
    await message.answer('готово')
    async with state.proxy() as data:
        data['price'] = int(message.text)
        data['id'] = message.from_user.id 
        d = await load_data(data)
        await Marketplace.sale_oil(data=d)
    await state.finish()

















async def load_data(data: dict):
    d = {
        'price': data['price'],
        'quantity': data['quantity'],
        'id': data['id']
    }
    print(d)
    return d
#data = FSMContext.get_data(MarketplaceStatesSaleFood)

# def register_handlers_market(dp: Dispatcher):
# dp.register_callback_query_handler(market_sale_food, text='marketseller_sale_food', state=None)
# dp.register_message_handler(market_sale_food, state=MarketplaceStates.quantity, content_types=['text'])
