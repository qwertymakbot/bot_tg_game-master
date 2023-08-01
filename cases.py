import random
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import asyncio

from bot import database, res_database
from create_bot import bot, dp, token


all_cars_data = list(database.cars.find())
cars_names_list = []
for car in list(database.cars.find()):
    cars_names_list.append(car['name_car'])

gcar = []
ecar = []
for car in list(database.cars.find()):
    if int(car['cost']) >= 20000:
        ecar.append(car['name_car'])
    elif int(car['cost']) <= 20000:
        gcar.append(car['name_car'])


class Database:
    def __init__(self):
        ...

    async def give_prize_in_little_case(self, callback: types.CallbackQuery, prize):
        user = database.users.find_one({'id': int(callback.from_user.id)})
        case_price = 10000
        database.users.update_one({'id': callback.from_user.id}, {'$set': {'cash': int(user['cash']) - case_price}})
        if '$' in prize[1]:
            database.users.update_one({'id': callback.from_user.id}, {'$set': {'cash': int(user['cash']) + prize[0]}})

        elif 'exp' in prize[1]:
            user_exp = int(user['exp'])
            database.users.update_one({'id': callback.from_user.id}, {'$set': {'exp': user_exp + prize[0]}})

    async def give_prize_in_middle_case(self, callback: types.CallbackQuery, prize):
        user = database.users.find_one({'id': int(callback.from_user.id)})
        case_price = 100000
        database.users.update_one({'id': callback.from_user.id}, {'$set': {'cash': int(user['cash']) - case_price}})
        if '$' in prize[1]:
            database.users.update_one({'id': callback.from_user.id}, {'$set': {'cash': int(user['cash']) + prize[0]}})

        elif 'exp' in prize[1]:
            database.users.update_one({'id': callback.from_user.id}, {'$set': {'exp': int(user['exp']) + prize[0]}})

        elif 'car' in prize[1]:
            car_info = database.cars.find_one({'name_car': prize[0]})
            user_cars = database.users_cars.find({'id': callback.from_user.id})
            if car_info['name'] in user_cars:
                await callback.message.answer(text=f'Вы выиграли машину которая уже присутствует в вашем гараже')
                return
            else:
                database.users_cars.insert_one({
                    'id': callback.from_user.id,
                    'car': prize[0],
                    'active': False,
                    'fuel_per_hour': car_info['fuel_per_hour']
                })


    async def give_prize_in_big_case(self, callback: types.CallbackQuery, prize):
        user = database.users.find_one({'id': int(callback.from_user.id)})
        case_price = 150000
        database.users.update_one({'id': callback.from_user.id}, {'$set': {'cash': int(user['cash']) - case_price}})
        if '$' in prize[1]:
            database.users.update_one({'id': callback.from_user.id}, {'$set': {'cash': int(user['cash']) + prize[0]}})

        elif 'exp' in prize[1]:
            database.users.update_one({'id': callback.from_user.id}, {'$set': {'exp': int(user['exp']) + prize[0]}})


        elif 'car' in prize[1]:
            car_info = database.cars.find_one({'name_car': prize[0]})
            user_cars = database.users_cars.find({'id': callback.from_user.id})
            if car_info['name'] in user_cars:
                await callback.message.answer(text=f'Вы выиграли машину которая уже присутствует в вашем гараже')
                return
            else:
                database.users_cars.insert_one({
                    'id': callback.from_user.id,
                    'car': prize[0],
                    'active': False,
                    'fuel_per_hour': car_info['fuel_per_hour']
                })


class Cases:

    def __init__(self):
        ...

    async def open_little_case(self):
        prizes = ['money', 'exp']
        prize = random.choice(prizes)

        match prize:
            case 'money':
                rand = random.randint(0, 4)
                if rand == 1:
                    money = random.randint(1000, 20000)
                    return [money, '$']
                else:
                    money = random.randint(100, 8000)
                    return [money, '$']

            case 'exp':
                rand = random.randint(0, 6)
                if rand == 1:
                    exp = random.randint(50, 1000)
                    return [exp, 'exp']
                else:
                    exp = random.randint(50, 200)
                    return [exp, 'exp']

    async def open_middle_case(self):
        prizes = ['car', 'money', 'exp', 'money', 'exp', 'money', 'exp']
        prize = random.choice(prizes)
        match prize:
            case 'money':
                rand = random.randint(0, 4)
                if rand == 1:
                    money = random.randint(1000, 50000)
                    return [money, '$']
                else:
                    money = random.randint(1000, 5000)
                    return [money, '$']

            case 'exp':
                rand = random.randint(0, 4)
                if rand == 1:
                    exp = random.randint(100, 1500)
                    return [exp, 'exp']
                else:
                    exp = random.randint(100, 500)
                    return [exp, 'exp']

            case 'car':
                rand = random.randint(0, 10)

                if rand == 1:
                    cars = ecar
                    car_name = random.choice(cars)
                    return [car_name, 'car']
                else:
                    cars = gcar
                    car_name = random.choice(cars)
                    return [car_name, 'car']
           #case 'class_in_school':
           #    rand = random.randint(0, 10)
           #    if rand == 1 or rand == 2:
           #        class_in_school = random.randint(0, 11)
           #        print(f"{username} выиграл переход на {class_in_school} класс школы ")
           #    else:
           #        print(f'{username} выиграл переход в следующий класс')

    async def open_big_case(self):
        prizes = ['car', 'money', 'exp', 'money', 'exp', 'money', 'exp']
        prize = random.choice(prizes)
        match prize:
            case 'money':
                rand = random.randint(0, 4)
                if rand == 1:
                    money = random.randint(1000, 200000)
                    return [money, '$']
                else:
                    money = random.randint(1000, 70000)
                    return [money, '$']

            case 'exp':
                rand = random.randint(0, 4)
                if rand == 1:
                    exp = random.randint(100, 1500)
                    return [exp, 'exp']
                else:
                    exp = random.randint(100, 500)
                    return [exp, 'exp']

            case 'car':
                rand = random.randint(0, 8)
                if rand == 1:
                    car_name = random.choice(ecar)
                    return [car_name, 'car']
                else:
                    car_name = random.choice(gcar)
                    return [car_name, 'car']

            #case 'class_in_school':
            #    rand = random.randint(0, 8)
            #    if rand == 1 or rand == 2:
            #        class_in_school = random.randint(0, 11)
            #        print(f"{username} выиграл переход на {class_in_school} класс школы ")
            #        return [class_in_school, 'class']
            #    else:
            #        print(f'{username} выиграл переход в следующий класс')
            #        return ['+1', 'class']


# ['ЕРАЗ 762', 'GEELY COOLRAY 2020', 'Agrale Marrua C87', 'McLaren 765LT', 'BMW M3 E36',
# 'BMW M3 E46 GTR', 'BMW M4 Competition', 'BMW M5 Competition', 'Ferrari 296 GTB 2022',
# 'KIA Soul 2022', 'BAIC Huansu S5', 'Spyker C12 Zagato', 'Lada Vesta', 'Dodge Challenger 2022 SRT',
# 'Audi A6', 'Audi R8', 'Mercedes-Benz G63 AMG 2018', 'Mercedes-Benz AMG GT 63s', 'Nissan GTR R34', 'Nissan GTR R35']


async def little_case(callback: types.CallbackQuery):
    db = Database()
    case = Cases()
    prize = await case.open_little_case()
    await db.give_prize_in_little_case(callback=callback, prize=prize)
    await bot.send_message(callback.message.chat.id, text=f'{callback.from_user.first_name} купил маленький кейс за 10000$')
    await bot.send_dice(callback.message.chat.id)
    await asyncio.sleep(4)
    await callback.message.answer( text=f'{callback.from_user.first_name} выбил {prize[0]}{prize[1]}')


async def middle_case(callback: types.CallbackQuery):
    db = Database()
    case = Cases()
    prize = await case.open_middle_case()
    await db.give_prize_in_middle_case(callback=callback, prize=prize)
    await callback.message.answer(text=f'{callback.from_user.first_name} купил средний кейс за 100000$')
    await bot.send_dice(callback.message.chat.id)
    await asyncio.sleep(4)
    if prize[1] == 'car':
        await callback.message.answer(text=f'{callback.from_user.first_name} выбил {prize[0]}')
    else:
        await callback.message.answer(text=f'{callback.from_user.first_name} выбил {prize[0]}{prize[1]}')


async def big_case(callback: types.CallbackQuery):
    db = Database()
    case = Cases()
    prize = await case.open_big_case()
    await db.give_prize_in_big_case(callback=callback, prize=prize)
    await callback.message.answer(text=f'{callback.from_user.first_name} Купил большой кейс за 150000$')
    await bot.send_dice(callback.message.chat.id)
    await asyncio.sleep(4)
    if prize[1] == 'car':
        await callback.message.answer(text=f'{callback.from_user.first_name} выбил {prize[0]}')
    else:
        await callback.message.answer(text=f'{callback.from_user.first_name} выбил {prize[0]}{prize[1]}')