from bot import check_user, types, InlineKeyboardButton, InlineKeyboardMarkup, database, bot, username, Dispatcher, InputFile
import os
from create_bot import dp



# /shop Магазин

async def shop(message: types.Message):
    await check_user(message)
    key = types.InlineKeyboardMarkup(row_width=1)
    # Категории в магазине
    cars = types.InlineKeyboardButton(text='Машины 🚗', callback_data='Магазин_машины')
    cases = types.InlineKeyboardButton(text='Кейсы 🎁', callback_data='Кейсы')
    marketplace = InlineKeyboardButton(text='Маркетплейс 💎', callback_data='marketplace_')
    key.add(cars, cases, marketplace)

    await bot.send_message(message.chat.id,
                           f'{await username(message)}, выберите категорию!', reply_markup=key, parse_mode='HTML')


@dp.callback_query_handler(text='Магазин_машины')
async def car(callback: types.CallbackQuery):
    user_info = database.users.find_one({'id': callback.from_user.id})
    if user_info['citizen_country'] != 'нет':
        cars_list = database.cars.find({'country': user_info['citizen_country']})
        key = InlineKeyboardMarkup(1)
        if len(list(cars_list)) == 0:
            await callback.message.edit_text(f'{await username(callback)} вашей стране нет доступных машин!', parse_mode='HTML')
            return
        for i in range(0, len(list(cars_list))):
            car = InlineKeyboardButton(text=f'{cars_list[i]["name_car"]} Цена: {cars_list[i]["cost"]}$',
                                       callback_data=f'shop_{cars_list[i]["name_car"]}')
            key.add(car)
        await callback.message.edit_text(f'{await username(callback)}, вам доступны следующие машины!', reply_markup=key, parse_mode='HTML')
    else:
        await callback.message.edit_text(
                               text=f'{await username(callback)}, вы не являетесь гражданином (/citizen)', parse_mode='HTML')

@dp.callback_query_handler(lambda callback: 'shop_' in callback.data)
async def buycar(callback: types.CallbackQuery):
    data_callback = callback.data
    user_id = callback.from_user.id
    # Покупка машины
    if 'shop_' in data_callback:
        data_callback = str(data_callback.replace('shop_', ''))
        user_info = database.users.find_one({'id': user_id})
        car_info = database.cars.find_one({'name_car': data_callback})
        if car_info['count'] == 0:
            await bot.send_message(callback.message.chat.id, message_thread_id=callback.message.message_thread_id,
                                   text=f'@{callback.from_user.username}, {car_info["name_car"]} нет в наличии!')
            return
        if user_info['cash'] >= car_info['cost']:
            count_user_car = database.users_cars.find_one({'id': user_id, 'car': car_info['name_car']})
            if count_user_car is None:
                database.users_cars.insert_one({'id': user_id,
                                                'car': car_info['name_car'],
                                                'color': car_info['color'],
                                                'cost': car_info['cost'],
                                                'country': car_info['country'],
                                                'oil': 0,
                                                'count': 1,
                                                'fuel_per_hour': car_info['fuel_per_hour'],
                                                'save_job_time': car_info['save_job_time'],
                                                'hp': car_info['hp'],
                                                'active': False})
                # -1 из наличия
                database.cars.update_one({'name_car': data_callback}, {'$set': {'count': car_info['count'] - 1}})
                # Снятие денег с баланса
                database.cars.update_one({'users': user_id}, {'$set': {'cash': user_info['cash'] - car_info['cost']}})
                # Зачисление денег на баланс государства
                country_info = database.countries.find_one({'country': car_info['country']})
                database.countries.update_one({'country': car_info['country']},
                                              {'$set': {'cash': country_info['cash'] + car_info['cost']}})
                await bot.send_photo(callback.message.chat.id, message_thread_id=callback.message.message_thread_id,
                                     caption=f'@{callback.from_user.username}, успешно приобрел машину!',
                                     photo=InputFile(
                                         f'{os.getcwd()}/res/cars_pic/{car_info["name_car"]} {car_info["color"]}.png'))

def register_handlers_shop(dp: Dispatcher):
    dp.register_message_handler(shop, text=['Магазин', 'магазин'])
    dp.register_message_handler(shop, commands='shop')
