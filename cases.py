import random
from aiogram import types


import asyncio

from bot import database,  username, InputFile
from create_bot import bot
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os

all_cars_data = list(database.cars.find())
cars_names_list = []
for car in list(database.cars.find()):
    cars_names_list.append(car['name_car'])

gcar = []
ecar = []
for car in list(database.cars.find()):
    if int(car['cost']) > 1_500_000:
        ecar.append(car['name_car'])
    elif int(car['cost']) <= 1_500_000:
        gcar.append(car['name_car'])


class Database:

    def __init__(self):
        ...

    @staticmethod
    async def give_prize_in_little_case(callback: types.CallbackQuery,
                                        prize):
        user = database.users.find_one({'id': int(callback.from_user.id)})
        case_price = 10_000
        database.users.update_one(
            {'id': callback.from_user.id},
            {'$set': {
                'cash': int(user['cash']) - case_price
            }})
        user = database.users.find_one({'id': int(callback.from_user.id)})
        if 'cash' in prize[1]:
            database.users.update_one(
                {'id': callback.from_user.id},
                {'$set': {
                    'cash': int(user['cash']) + prize[0]
                }})

        elif 'exp' in prize[1]:
            user_exp = int(user['exp'])
            database.users.update_one({'id': callback.from_user.id},
                                      {'$set': {
                                          'exp': user_exp + prize[0]
                                      }})

    @staticmethod
    async def give_prize_in_middle_case(callback: types.CallbackQuery,
                                        prize):
        user = database.users.find_one({'id': int(callback.from_user.id)})
        user_education = database.education.find_one({'id': callback.from_user.id})
        case_price = 500_000
        database.users.update_one(
            {'id': callback.from_user.id},
            {'$set': {
                'cash': int(user['cash']) - case_price
            }})
        user = database.users.find_one({'id': int(callback.from_user.id)})
        if 'cash' in prize[1]:
            database.users.update_one(
                {'id': callback.from_user.id},
                {'$set': {
                    'cash': int(user['cash']) + prize[0]
                }})

        elif 'exp' in prize[1]:
            database.users.update_one(
                {'id': callback.from_user.id},
                {'$set': {
                    'exp': int(user['exp']) + prize[0]
                }})

        elif 'car' in prize[1]:
            car_info = database.cars.find_one({'name_car': prize[0]})
            user_cars = database.users_cars.find({'id': callback.from_user.id})
            if car_info['name_car'] in user_cars:
                database.users.update_one(
                    {'id': callback.from_user.id},
                    {'$set': {
                        'cash': user['cash'] + car_info['cost']
                    }})
                await bot.send_message(
                    callback.message.chat.id,
                    f'{await username(callback)}, данная модель уже есть в вашем гараже, вы получите компенсацию!',
                    parse_mode='HTML')
                return
            else:
                database.users_cars.insert_one({
                    'id':
                    callback.from_user.id,
                    'car':
                    prize[0],
                    'active':
                    False,
                    'fuel_per_hour':
                    car_info['fuel_per_hour'],
                    'save_job_time':
                    car_info['save_job_time'],
                    'cost':
                    car_info['cost'],
                    'hp':
                    car_info['hp']
                })
        elif 'license' in prize[1]:
            if user_education['auto_school'] == 'нет' and user_education['status'] == 'окончил':
                database.education.update_one({'id': int(callback.from_user.id)},
                                              {'$set': {
                                                  'auto_school': 'да'
                                              }})
            else:
                if user_education['auto_school'] == 'нет' and user_education['status'] == 'нет':
                    database.users.update_one({'id': int(callback.from_user.id)}, {
                        '$set': {
                            'cash': user['cash'] + 100_000,
                            'exp': user['exp'] + 5_000
                        }
                    })
                    await bot.send_message(
                        callback.message.chat.id,
                        f'{await username(callback)}, вы еще не окончили обучение в школе, вы получите компенсацию в размере 100 000$ и 5 000exp!',
                        parse_mode='HTML')
                elif user_education['auto_school'] == 'да':
                    database.users.update_one({'id': int(callback.from_user.id)}, {
                        '$set': {
                            'cash': user['cash'] + 100_000,
                            'exp': user['exp'] + 5_000
                        }
                    })
                    await bot.send_message(
                        callback.message.chat.id,
                        f'{await username(callback)}, у вас уже имеются права, вы получите компенсацию в размере 100 000$ и 5 000exp!',
                        parse_mode='HTML')

    @staticmethod
    async def give_prize_in_big_case(callback: types.CallbackQuery,
                                     prize):
        user = database.users.find_one({'id': int(callback.from_user.id)})
        case_price = 1_500_000
        database.users.update_one(
            {'id': callback.from_user.id},
            {'$set': {
                'cash': int(user['cash']) - case_price
            }})
        user = database.users.find_one({'id': int(callback.from_user.id)})
        if 'cash' in prize[1]:
            database.users.update_one(
                {'id': callback.from_user.id},
                {'$set': {
                    'cash': int(user['cash']) + prize[0]
                }})
        elif 'exp' in prize[1]:
            database.users.update_one(
                {'id': callback.from_user.id},
                {'$set': {
                    'exp': int(user['exp']) + prize[0]
                }})
        elif 'car' in prize[1]:
            car_info = database.cars.find_one({'name_car': prize[0]})
            user_cars = database.users_cars.find({'id': callback.from_user.id})
            if car_info['name_car'] in user_cars:
                database.users.update_one(
                    {'id': callback.from_user.id},
                    {'$set': {
                        'cash': user['cash'] + car_info['cost']
                    }})
                await bot.send_message(
                    callback.message.chat.id,
                    f'{await username(callback)}, данная модель уже есть в вашем гараже, вы получите компенсацию!',
                    parse_mode='HTML')
                return
            else:
                database.users_cars.insert_one({
                    'id':
                    callback.from_user.id,
                    'car':
                    prize[0],
                    'active':
                    False,
                    'fuel_per_hour':
                    car_info['fuel_per_hour'],
                    'save_job_time':
                    car_info['save_job_time'],
                    'cost':
                    car_info['cost'],
                    'hp':
                    car_info['hp']
                })
        elif 'country' in prize[1]:
            if prize[0] == 'нет':
                database.users.update_one(
                    {'id': callback.from_user.id},
                    {'$set': {
                        'cash': user['cash'] + 3_000_000
                    }})
                await bot.send_message(
                    callback.message.chat.id,
                    f'{await username(callback)}, нет свободных стран, поэтому вам выдана компенсация!',
                    parse_mode='HTML')
                return
            else:
                database.users.update_one({'id': callback.from_user.id}, {
                    '$set': {
                        'president_country': prize[0],
                        'citizen_country': prize[0]
                    }
                })
                database.countries.update_one(
                    {'country': prize[0]},
                    {'$set': {
                        'president': callback.from_user.id
                    }})


class Cases:

    def __init__(self):
        ...

    @staticmethod
    async def open_little_case():
        prizes = ['money', 'exp']
        prize = random.choice(prizes)

        match prize:
            case 'money':
                rand = random.randint(0, 10)
                if rand == 1:
                    money = random.randint(8000, 100000)
                    return [money, 'cash']
                else:
                    money = random.randint(100, 8000)
                    return [money, 'cash']

            case 'exp':
                rand = random.randint(0, 10)
                if rand == 1:
                    exp = random.randint(1000, 10000)
                    return [exp, 'exp']
                else:
                    exp = random.randint(50, 1000)
                    return [exp, 'exp']

    @staticmethod
    async def open_middle_case():
        prizes = [
            'car', 'money', 'money', 'exp', 'money', 'exp', 'exp', 'money', 'exp', 'money', 'exp', 'money', 'exp', 'license'
        ]
        prize = random.choice(prizes)
        match prize:
            case 'money':
                rand = random.randint(0, 8)
                if rand == 1:
                    money = random.randint(700_000, 1_500_000)
                    return [money, 'cash']
                else:
                    money = random.randint(100_000, 700_000)
                    return [money, 'cash']

            case 'exp':
                rand = random.randint(0, 8)
                if rand == 1:
                    exp = random.randint(7000, 15000)
                    return [exp, 'exp']
                else:
                    exp = random.randint(100, 6300)
                    return [exp, 'exp']

            case 'car':
                rand = random.randint(0, 20)

                if rand == 1:
                    cars = ecar
                    car_name = random.choice(cars)
                    return [car_name, 'car']
                else:
                    cars = gcar
                    car_name = random.choice(cars)
                    return [car_name, 'car']
            case 'license':
                return ['Права B категории', 'license']
        #case 'class_in_school':
        #    rand = random.randint(0, 10)
        #    if rand == 1 or rand == 2:
        #        class_in_school = random.randint(0, 11)
        #        print(f"{username} выиграл переход на {class_in_school} класс школы ")
        #    else:
        #        print(f'{username} выиграл переход в следующий класс')

    @staticmethod
    async def open_big_case(user_id: int) -> None:
        user = database.users.find_one({'id': int(user_id)})
        if user is not None:
            if str(user['president_country']) == 'нет':
                prizes = [
                            'car', 'money', 'exp', 'money', 'exp', 'money', 'exp', 'money', 'money', 'exp', 'money', 'exp', 'money', 'exp',
                            'exp', 'country'
                        ]
            elif str(user['president_country']) != 'нет':
                prizes = [
                            'car', 'money', 'exp', 'money', 'exp', 'money', 'exp', 'money',
                            'exp', 'money'
                        ]
        prize = random.choice(prizes)
        match prize:
            case 'money':
                rand = random.randint(0, 8)
                if rand == 1:
                    money = random.randint(2_000_000, 10_000_000)
                    return [money, 'cash']
                else:
                    money = random.randint(650_000, 2_000_000)
                    return [money, 'cash']

            case 'exp':
                rand = random.randint(0, 8)
                if rand == 1:
                    exp = random.randint(30000, 80000)
                    return [exp, 'exp']
                else:
                    exp = random.randint(8000, 30000)
                    return [exp, 'exp']

            case 'car':
                rand = random.randint(0, 8)
                if rand == 1:
                    car_name = random.choice(ecar)
                    return [car_name, 'car']
                else:
                    car_name = random.choice(gcar)
                    return [car_name, 'car']
            case 'country':
                country_list = list(database.countries.find({'president': 0}))
                if country_list:
                    country = random.choice(country_list)
                    return [country['country'], 'country']
                else:
                    return ['нет', 'country']


async def little_case(callback: types.CallbackQuery):
    db = Database()
    case = Cases()
    user = database.users.find_one({'id': int(callback.from_user.id)})
    case_price = 10000
    if user['cash'] >= case_price:
        prize = await case.open_little_case()

        await bot.send_message(
            callback.message.chat.id,
            f'{await username(callback)} купил маленький кейс за 10 000 $',
            parse_mode='HTML')
        await bot.send_dice(callback.message.chat.id)
        await asyncio.sleep(3)
        if prize[1] == 'cash':
            img = Image.open(
                f'{os.getcwd()}/res/case_pic/little_money.png').convert("RGBA")
            font = ImageFont.truetype(
                f'{os.getcwd()}/res/fonts/Blogger_Sans.otf', size=85)
            draw_text = ImageDraw.Draw(img)
            # опыт
            draw_text.text((1270, 475),
                           f'+{prize[0]} $',
                           font=font,
                           fill='#62ca29')
            img.save(f'{os.getcwd()}/res/case_pic/cache/little.png')
            await bot.send_photo(
                callback.message.chat.id,
                photo=InputFile(f'{os.getcwd()}/res/case_pic/cache/little.png',
                                filename='case_little'),
                caption=f'{await username(callback)}, вы выиграли деньги!',
                parse_mode='HTML')
        if prize[1] == 'exp':
            img = Image.open(
                f'{os.getcwd()}/res/case_pic/little_exp.png').convert("RGBA")
            font = ImageFont.truetype(
                f'{os.getcwd()}/res/fonts/Blogger_Sans.otf', size=85)
            draw_text = ImageDraw.Draw(img)
            # опыт
            draw_text.text((1270, 475),
                           f'+{prize[0]}',
                           font=font,
                           fill='#62ca29')
            img.save(f'{os.getcwd()}/res/case_pic/cache/little.png')
            await bot.send_photo(
                callback.message.chat.id,
                photo=InputFile(f'{os.getcwd()}/res/case_pic/cache/little.png',
                                filename='case_little'),
                caption=f'{await username(callback)}, вы выиграли опыт!',
                parse_mode='HTML')
        # Начисление награды
        await db.give_prize_in_little_case(callback=callback, prize=prize)
    else:
        await bot.send_message(
            callback.message.chat.id,
            f'{await username(callback)}, у вас недостаточно средств!',
            parse_mode='HTML')


async def middle_case(callback: types.CallbackQuery):
    db = Database()
    case = Cases()
    user = database.users.find_one({'id': int(callback.from_user.id)})
    case_price = 500_000
    if user['cash'] >= case_price:
        prize = await case.open_middle_case()

        await bot.send_message(
            callback.message.chat.id,
            f'{await username(callback)} купил средний кейс за 500 000 $',
            parse_mode='HTML')
        await bot.send_dice(callback.message.chat.id)
        await asyncio.sleep(3)
        if prize[1] == 'cash':
            img = Image.open(
                f'{os.getcwd()}/res/case_pic/middle_money.png').convert("RGBA")
            font = ImageFont.truetype(
                f'{os.getcwd()}/res/fonts/Blogger_Sans.otf', size=85)
            draw_text = ImageDraw.Draw(img)
            # опыт
            draw_text.text((1270, 475),
                           f'+{prize[0]} $',
                           font=font,
                           fill='#62ca29')
            img.save(f'{os.getcwd()}/res/case_pic/cache/middle.png')
            await bot.send_photo(
                callback.message.chat.id,
                photo=InputFile(f'{os.getcwd()}/res/case_pic/cache/middle.png',
                                filename='case_middle'),
                caption=f'{await username(callback)}, вы выиграли деньги!',
                parse_mode='HTML')
        if prize[1] == 'exp':
            img = Image.open(
                f'{os.getcwd()}/res/case_pic/middle_exp.png').convert("RGBA")
            font = ImageFont.truetype(
                f'{os.getcwd()}/res/fonts/Blogger_Sans.otf', size=85)
            draw_text = ImageDraw.Draw(img)
            # опыт
            draw_text.text((1270, 475),
                           f'+{prize[0]}',
                           font=font,
                           fill='#62ca29')
            img.save(f'{os.getcwd()}/res/case_pic/cache/middle.png')
            await bot.send_photo(
                callback.message.chat.id,
                photo=InputFile(f'{os.getcwd()}/res/case_pic/cache/middle.png',
                                filename='case_middle'),
                caption=f'{await username(callback)}, вы выиграли опыт!',
                parse_mode='HTML')

        if prize[1] == 'car':
            img = Image.open(
                f'{os.getcwd()}/res/case_pic/middle_car.png').convert("RGBA")
            font = ImageFont.truetype(
                f'{os.getcwd()}/res/fonts/Blogger_Sans.otf', size=50)
            draw_text = ImageDraw.Draw(img)
            # опыт
            draw_text.text((1200, 485),
                           f'{prize[0]}',
                           font=font,
                           fill='#62ca29')
            img.save(f'{os.getcwd()}/res/case_pic/cache/middle.png')
            await bot.send_photo(
                callback.message.chat.id,
                photo=InputFile(f'{os.getcwd()}/res/case_pic/cache/middle.png',
                                filename='case_middle'),
                caption=f'{await username(callback)}, вы выиграли автомобиль!',
                parse_mode='HTML')
        if prize[1] == 'license':
            # фото профиля
            user_profile_photo = await bot.get_user_profile_photos(
                callback.from_user.id, limit=1)
            if user_profile_photo.photos:
                file = await bot.get_file(
                    user_profile_photo.photos[0][0].file_id)
                await bot.download_file(
                    file.file_path,
                    f'{os.getcwd()}/res/case_pic/cache/profile.png')
                img_profile = Image.open(
                    f'{os.getcwd()}/res/case_pic/cache/profile.png').convert(
                        "RGBA")
                img = Image.open(f'{os.getcwd()}/res/case_pic/middle_drive.png'
                                 ).convert("RGBA")
                font = ImageFont.truetype(
                    f'{os.getcwd()}/res/fonts/Blogger_Sans.otf', size=68)
                draw_text = ImageDraw.Draw(img)
                draw_text.text((1270, 475),
                               f'{prize[0]}',
                               font=font,
                               fill='#62ca29')
                new_img_profile = img_profile.resize((170, 184))
                img.paste(new_img_profile, (309, 350))
                img.save(f'{os.getcwd()}/res/case_pic/cache/middle.png')
                await bot.send_photo(
                    callback.message.chat.id,
                    photo=InputFile(
                        f'{os.getcwd()}/res/case_pic/cache/middle.png',
                        filename='case_middle'),
                    caption=f'{await username(callback)}, вы выиграли права!',
                    parse_mode='HTML')
            else:
                img = Image.open(f'{os.getcwd()}/res/case_pic/middle_drive.png'
                                 ).convert("RGBA")
                font = ImageFont.truetype(
                    f'{os.getcwd()}/res/fonts/Blogger_Sans.otf', size=68)
                draw_text = ImageDraw.Draw(img)
                draw_text.text((1270, 475),
                               f'{prize[0]}',
                               font=font,
                               fill='#62ca29')
                img.save(f'{os.getcwd()}/res/case_pic/cache/middle.png')
                await bot.send_photo(
                    callback.message.chat.id,
                    photo=InputFile(
                        f'{os.getcwd()}/res/case_pic/cache/middle.png',
                        filename='case_middle'),
                    caption=f'{await username(callback)}, вы выиграли права!',
                    parse_mode='HTML')
        # Начисление награды
        await db.give_prize_in_middle_case(callback=callback, prize=prize)

    else:
        await bot.send_message(
            callback.message.chat.id,
            f'{await username(callback)}, у вас недостаточно средств!',
            parse_mode='HTML')


async def big_case(callback: types.CallbackQuery):
    db = Database()
    case = Cases()
    user = database.users.find_one({'id': int(callback.from_user.id)})
    case_price = 1_500_000
    if user['cash'] >= case_price:
        prize = await case.open_big_case(user_id=callback.from_user.id)

        await bot.send_message(
            callback.message.chat.id,
            f'{await username(callback)} купил большой кейс за 1 500 000 $',
            parse_mode='HTML')
        await bot.send_dice(callback.message.chat.id)
        await asyncio.sleep(3)
        if prize[1] == 'cash':
            img = Image.open(
                f'{os.getcwd()}/res/case_pic/big_money.png').convert("RGBA")
            font = ImageFont.truetype(
                f'{os.getcwd()}/res/fonts/Blogger_Sans.otf', size=85)
            draw_text = ImageDraw.Draw(img)
            # опыт
            draw_text.text((1270, 475),
                           f'+{prize[0]} $',
                           font=font,
                           fill='#62ca29')
            img.save(f'{os.getcwd()}/res/case_pic/cache/big.png')
            await bot.send_photo(
                callback.message.chat.id,
                photo=InputFile(f'{os.getcwd()}/res/case_pic/cache/big.png',
                                filename='case_big'),
                caption=f'{await username(callback)}, вы выиграли деньги!',
                parse_mode='HTML')
        if prize[1] == 'exp':
            img = Image.open(
                f'{os.getcwd()}/res/case_pic/big_exp.png').convert("RGBA")
            font = ImageFont.truetype(
                f'{os.getcwd()}/res/fonts/Blogger_Sans.otf', size=85)
            draw_text = ImageDraw.Draw(img)
            # опыт
            draw_text.text((1270, 475),
                           f'+{prize[0]}',
                           font=font,
                           fill='#62ca29')
            img.save(f'{os.getcwd()}/res/case_pic/cache/big.png')
            await bot.send_photo(
                callback.message.chat.id,
                photo=InputFile(f'{os.getcwd()}/res/case_pic/cache/big.png',
                                filename='case_big'),
                caption=f'{await username(callback)}, вы выиграли опыт!',
                parse_mode='HTML')

        if prize[1] == 'car':
            img = Image.open(
                f'{os.getcwd()}/res/case_pic/big_car.png').convert("RGBA")
            font = ImageFont.truetype(
                f'{os.getcwd()}/res/fonts/Blogger_Sans.otf', size=50)
            draw_text = ImageDraw.Draw(img)
            # опыт
            draw_text.text((1200, 485),
                           f'{prize[0]}',
                           font=font,
                           fill='#62ca29')
            img.save(f'{os.getcwd()}/res/case_pic/cache/big.png')
            await bot.send_photo(
                callback.message.chat.id,
                photo=InputFile(f'{os.getcwd()}/res/case_pic/cache/big.png',
                                filename='case_big'),
                caption=f'{await username(callback)}, вы выиграли автомобиль!',
                parse_mode='HTML')

        if prize[1] == 'country':
            img = Image.open(
                f'{os.getcwd()}/res/case_pic/big_country.png').convert("RGBA")
            font = ImageFont.truetype(
                f'{os.getcwd()}/res/fonts/Blogger_Sans.otf', size=85)
            draw_text = ImageDraw.Draw(img)
            # страна
            if prize[0] != 'нет':
                draw_text.text((1270, 475),
                               f'{prize[0]}',
                               font=font,
                               fill='#62ca29')
                img.save(f'{os.getcwd()}/res/case_pic/cache/big.png')

                await bot.send_photo(
                    callback.message.chat.id,
                    photo=InputFile(f'{os.getcwd()}/res/case_pic/cache/big.png',
                                    filename='case_big'),
                    caption=f'{await username(callback)}, вы выиграли страну!',
                    parse_mode='HTML')
            else:
                draw_text.text((1270, 475),
                               f'компенсация',
                               font=font,
                               fill='#62ca29')
                img.save(f'{os.getcwd()}/res/case_pic/cache/big.png')

                await bot.send_photo(
                    callback.message.chat.id,
                    photo=InputFile(f'{os.getcwd()}/res/case_pic/cache/big.png',
                                    filename='case_big'),
                    caption=f'{await username(callback)}, вы выиграли компенсацию!',
                    parse_mode='HTML')

        # Начисление награды
        await db.give_prize_in_big_case(callback=callback, prize=prize)
    else:
        await bot.send_message(
            callback.message.chat.id,
            f'{await username(callback)}, у вас недостаточно средств!',
            parse_mode='HTML')
