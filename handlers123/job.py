import datetime
import json
import os
import re
from bot import check_user, scheduler, Dispatcher, bot, types, tag_user, InputFile, InlineKeyboardButton, \
    InlineKeyboardMarkup, database, res_database, username, add_time_min, username_2
import pytz
from dateutil import parser
import random
import asyncio

food_mak = 20
food_povar = 45
food_pekar = 35
food_fermer = 100


# /work Работать
async def work(message: types.Message):
    await check_user(message)
    user_id = message.from_user.id
    user_info = database.users.find_one({'id': user_id})
    res_job_info = res_database.job.find_one({'id': user_id})
    res_disease_info = res_database.disease.find_one({'id': user_id})
    if user_info["job"] != 'нет':  # Если есть работа
        if res_job_info and res_job_info['working']:
            # Получение переменных с строки
            tz = pytz.timezone('Etc/GMT-3')
            date, time = res_job_info['time'].split(' ')
            year, month, day = date.split('-')
            hour, minute, second = time.split(':')
            time_job = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
            time_now = datetime.datetime(datetime.datetime.now(tz=tz).year, datetime.datetime.now(tz=tz).month,
                                         datetime.datetime.now(tz=tz).day, datetime.datetime.now(tz=tz).hour,
                                         datetime.datetime.now(tz=tz).minute, datetime.datetime.now(tz=tz).second)
            result = time_job - time_now
            # Если уже отработал
            if '-' in str(result):
                res_database.job.update_one({'id': user_id}, {'$set': {'working': False}})
                await work(message)
            else:
                await bot.send_message(message.chat.id,
                                       f'{await username(message)}, вы уже работаете, вам ещё осталось {result}',
                                       parse_mode='HTML')
            return
        else:
            if res_disease_info is not None:  # Если есть болезнь
                # Получение переменных с строки
                tz = pytz.timezone('Etc/GMT-3')
                date, time = res_disease_info['time'].split(' ')
                year, month, day = date.split('-')
                hour, minute, second = time.split(':')
                time_disease = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
                time_now = datetime.datetime(datetime.datetime.now(tz=tz).year, datetime.datetime.now(tz=tz).month,
                                             datetime.datetime.now(tz=tz).day, datetime.datetime.now(tz=tz).hour,
                                             datetime.datetime.now(tz=tz).minute, datetime.datetime.now(tz=tz).second)
                result = time_disease - time_now
                # Если уже отболел
                if '-' in str(result):
                    res_database.disease.delete_one({'id': user_id})
                    await work(message)
                else:

                    await bot.send_message(message.chat.id,
                                       f'{await username(message)}, вам ещё осталось болеть {result} 🦠',
                                       parse_mode='HTML')
            else:
                rand_num = random.randint(1, 10)
                if rand_num == 1:  # Если заболел

                    all_diseases = database.diseases.find()
                    disease_info = random.choice(list(all_diseases))

                    # Добавление в бд инфы о болезни
                    res_database.disease.insert_one({'id': user_id,
                                                     'time': await add_time_min(disease_info['time']),
                                                     'disease': True})
                    tz = pytz.timezone('Etc/GMT-3')
                    scheduler.add_job(end_disease, "date",
                                      run_date=await add_time_min(disease_info['time']),
                                      args=(message,), id=str(user_id), timezone=tz)
                    await bot.send_message(message.chat.id,
                                           f'{await username(message)}, вы заболели болезнью {disease_info["disease"].lower()} на время {disease_info["time"]} минут 🦠',
                                           parse_mode='HTML')
                else:
                    if user_info['citizen_country'] != 'нет':  # Если гражданин
                        job_info = database.jobs.find_one({'name_job': user_info['job']})
                        country_info = database.countries.find_one({'country': user_info['citizen_country']})
                        if country_info['food'] >= job_info['need_food']:  # Если в стране достаточно еды
                            # Если в стране < 50
                            if country_info['food'] < 50:
                                if res_database.country_check_food.find_one({'id': country_info["president"]}) is None:
                                    # SCHEDULER
                                    res_database.country_check_food.insert_one({'id': country_info["president"],
                                                                                'time': await add_time_min(1440)})

                                    tz = pytz.timezone('Etc/GMT-3')
                                    scheduler.add_job(check_food_country, "date",
                                                      run_date=await add_time_min(job_info['job_time']),
                                                      args=(country_info["president"],), timezone=tz)
                                    await bot.send_message(country_info['president'],
                                                           f'{await username_2(country_info["president"], database.users.find_one({"id": country_info["president"]})["firstname"])}, в вашей стране осталось меньше 50 кг еды!\n'
                                                           f'Если не будут приняты меры по восстановлению еды, то через 24 часа страна будет отобрана и средства возмещены не будут!\n'
                                                           f'Просьба принять меры!', parse_mode='HTML')

                            arr = next(os.walk(f'{os.getcwd()}/res/jobs_pic/{user_info["job"]}'))[2]
                            # Если строитель, то не работаем
                            if user_info['job'] == 'Строитель':
                                builder_info = database.builders_work.find_one({'id': user_id})
                                if builder_info is not None:
                                    await message.answer(
                                        f'{await username(message)}, сначала завершите либо покиньте стройку',
                                        parse_mode='HTML')
                                    return

                            # Автосборщик
                            if user_info['job'] == 'Автосборщик':
                                autocreater_work = database.autocreater_work.find_one({'creater': message.from_user.id})
                                if autocreater_work is not None:
                                    # Снятие еды со страны за работу
                                    database.countries.update_one({'country': user_info['citizen_country']},
                                                                  {'$set': {'food': country_info['food'] - job_info[
                                                                      'need_food']}})
                                    await bot.send_photo(message.chat.id,
                                                         photo=InputFile(
                                                             f'{os.getcwd()}/res/jobs_pic/{user_info["job"]}/{random.choice(arr)}'),
                                                         caption=f'{await username(message)}, вы начали работать по профессии {user_info["job"].lower()}\n'
                                                                 f'Через {job_info["job_time"]} минут вы закончите!',
                                                         parse_mode='HTML')
                                    # SCHEDULER
                                    res_database.job.update_one({'id': user_id},
                                                                {'$set': {
                                                                    'time': await add_time_min(job_info['job_time']),
                                                                    'working': True}})

                                    tz = pytz.timezone('Etc/GMT-3')
                                    scheduler.add_job(end_job_citizen, "date",
                                                      run_date=await add_time_min(job_info['job_time']),
                                                      args=(message, user_info['job']), id=str(user_id), timezone=tz)
                                else:
                                    await bot.send_message(message.chat.id,
                                                           f'{await username(message)}, для начала вам нужно устроится в автосборку!')
                                return

                            # Снятие еды со страны за работу
                            database.countries.update_one({'country': user_info['citizen_country']},
                                                          {'$set': {
                                                              'food': country_info['food'] - job_info['need_food']}})
                            # Если есть машина
                            car_info = database.users_cars.find_one({'$and': [{'id': user_id}, {'active': True}]})
                            if car_info is not None:
                                need_oil = round(car_info['fuel_per_hour'] / (60 / job_info['job_time']))
                                if user_info['oil'] >= need_oil:
                                    # Сжигаем топливо
                                    database.users.update_one(
                                        {'id': user_id},
                                        {'$set': {'oil': user_info['oil'] - need_oil}})
                                    # Вычисление времени на работу едя на машине
                                    job_time = job_info['job_time'] - round(job_info['job_time'] * (car_info['save_job_time'] / 100))
                                    await bot.send_photo(message.chat.id,
                                                         photo=InputFile(
                                                             f'{os.getcwd()}/res/jobs_pic/{user_info["job"]}/{random.choice(arr)}'),
                                                         caption=f'{await username(message)}, вы поехали на машине и начали работать по профессии {user_info["job"].lower()}\n'
                                                                 f'Через {job_time} минут вы закончите!\n'
                                                                 f'Вы потратили:\n'
                                                                 f'🖤 -{need_oil}л', parse_mode='HTML')
                                    # SCHEDULER
                                    res_database.job.update_one({'id': user_id},
                                                                {'$set': {'time': await add_time_min(job_time),
                                                                          'working': True}})
                                    tz = pytz.timezone('Etc/GMT-3')
                                    scheduler.add_job(end_job_citizen, "date",
                                                      run_date=await add_time_min(job_time),
                                                      args=(message, user_info['job']), id=str(user_id), timezone=tz)
                                # Если нет топлива
                                else:
                                    await bot.send_photo(message.chat.id,
                                                         photo=InputFile(
                                                             f'{os.getcwd()}/res/jobs_pic/{user_info["job"]}/{random.choice(arr)}'),
                                                         caption=f'{await username(message)}, в вашем {car_info["car"]} недостаточно топлива, вы пошли на работу пешком и начали работать по профессии {user_info["job"].lower()}\n'
                                                                 f'Через {job_info["job_time"]} минут вы закончите!',
                                                         parse_mode='HTML')
                                    # SCHEDULER
                                    res_database.job.update_one({'id': user_id},
                                                                {'$set': {
                                                                    'time': await add_time_min(job_info['job_time']),
                                                                    'working': True}})

                                    tz = pytz.timezone('Etc/GMT-3')
                                    scheduler.add_job(end_job_citizen, "date",
                                                      run_date=await add_time_min(job_info['job_time']),
                                                      args=(message, user_info['job']), id=str(user_id), timezone=tz)
                            # Если нет машины
                            else:
                                await bot.send_photo(message.chat.id,
                                                     photo=InputFile(
                                                         f'{os.getcwd()}/res/jobs_pic/{user_info["job"]}/{random.choice(arr)}'),
                                                     caption=f'{await username(message)}, вы начали работать по профессии {user_info["job"].lower()}\n'
                                                             f'Через {job_info["job_time"]} минут вы закончите!',
                                                     parse_mode='HTML')
                                # SCHEDULER
                                res_database.job.update_one({'id': user_id},
                                                            {'$set': {'time': await add_time_min(job_info['job_time']),
                                                                      'working': True}})

                                tz = pytz.timezone('Etc/GMT-3')
                                scheduler.add_job(end_job_citizen, "date",
                                                  run_date=await add_time_min(job_info['job_time']),
                                                  args=(message, user_info['job']), id=str(user_id), timezone=tz)
                        else:
                            await bot.send_message(message.chat.id,
                                                   f'{await username(message)}, в вашей стране недостаточно еды!',
                                                   parse_mode='HTML')
                    else:  # Если не гражданин
                        job_info = database.jobs.find_one({'name_job': user_info['job']})
                        if user_info['food'] >= job_info['need_food']:
                            arr = next(os.walk(f'{os.getcwd()}/res/jobs_pic/{user_info["job"]}'))[2]
                            # Если есть машина
                            car_info = database.users_cars.find_one({'$and': [{'id': user_id}, {'active': True}]})
                            if car_info is not None:
                                need_oil = round(car_info['fuel_per_hour'] / (60 / job_info['job_time']))
                                if user_info['oil'] >= need_oil:
                                    # Сжигаем топливо
                                    database.users.update_one(
                                        {'id': user_id},
                                        {'$set': {'oil': user_info['oil'] - need_oil}})
                                    # Вычисление времени на работу едя на машине
                                    job_time = job_info['job_time'] - round(job_info['job_time'] * (car_info['save_job_time'] / 100))

                                    await bot.send_photo(message.chat.id,
                                                         photo=InputFile(
                                                             f'{os.getcwd()}/res/jobs_pic/{user_info["job"]}/{random.choice(arr)}'),
                                                         caption=f'{await username(message)}, вы поехали на машине и начали работать по профессии {user_info["job"].lower()}\n'
                                                                 f'Через {job_time} минут вы закончите!\n'
                                                                 f'Вы потратили:\n'
                                                                 f'🖤 -{need_oil}л', parse_mode='HTML')
                                    # SCHEDULER
                                    res_database.job.update_one({'id': user_id},
                                                                {'$set': {'time': await add_time_min(job_time),
                                                                          'working': True}})
                                    tz = pytz.timezone('Etc/GMT-3')
                                    scheduler.add_job(end_job_no_citizen, "date",
                                                      run_date=await add_time_min(job_info['job_time']),
                                                      args=(message, user_info['job']), id=str(user_id), timezone=tz)
                                # Если нет топлива
                                else:
                                    await bot.send_photo(message.chat.id,
                                                         photo=InputFile(
                                                             f'{os.getcwd()}/res/jobs_pic/{user_info["job"]}/{random.choice(arr)}'),
                                                         caption=f'{await username(message)}, в вашем {car_info["car"]} недостаточно топлива, вы пошли на работу пешком и начали работать по профессии {user_info["job"].lower()}\n'
                                                                 f'Через {job_info["job_time"]} минут вы закончите!',
                                                         parse_mode='HTML')
                                    # SCHEDULER
                                    res_database.job.update_one({'id': user_id},
                                                                {'$set': {
                                                                    'time': await add_time_min(job_info['job_time']),
                                                                    'working': True}})

                                    tz = pytz.timezone('Etc/GMT-3')
                                    scheduler.add_job(end_job_no_citizen, "date",
                                                      run_date=await add_time_min(job_info['job_time']),
                                                      args=(message, user_info['job']), id=str(user_id), timezone=tz)
                            else:
                                res_database.job.update_one({'id': user_id},
                                                            {'$set': {'time': await add_time_min(job_info['job_time']),
                                                                      'working': True}})
                                tz = pytz.timezone('Etc/GMT-3')
                                scheduler.add_job(end_job_no_citizen, "date", run_date=await add_time_min(job_info['job_time']),
                                                  args=(message, user_info['job']), id=str(user_id), timezone=tz)

                                await bot.send_photo(message.chat.id,
                                                     photo=InputFile(
                                                         f'{os.getcwd()}/res/jobs_pic/{user_info["job"]}/{random.choice(arr)}'),
                                                     caption=f'{await username(message)}, вы начали работать по профессии {user_info["job"].lower()}\n'
                                                             f'Через {job_info["job_time"]} минут вы закончите!',
                                                     parse_mode='HTML')
                        else:
                            await bot.send_message(message.chat.id, f'{await username(message)}, у вас недостаточно еды!', parse_mode='HTML')
    else:
        await bot.send_message(message.chat.id, f'{await username(message)}, вы нигде не работаете!', parse_mode='HTML')


# /jobs Устроится на работу
async def getjob(message: types.Message):
    await check_user(message)
    educ_info = database.education.find_one({'id': message.from_user.id})
    if educ_info is not None:
        buttons = InlineKeyboardMarkup(1)
        jobs = re.split(r"\s+(?=[А-Я])", educ_info['jobs'])
        for job in jobs:
            buttons.add(InlineKeyboardButton(job, callback_data=f'getjob_{job}_{str(message.from_user.id)[-2::]}'))
        await bot.send_message(message.chat.id, text='❗️ Чтобы открыть больше введите /education\n'
                                                     '🛠 Список доступных работ 🛠', reply_markup=buttons)
    else:
        buttons = InlineKeyboardMarkup(1)
        jobs = ['Раб', 'Дворник', 'Дояр']
        for job in jobs:
            buttons.add(InlineKeyboardButton(job, callback_data=f'getjob_{job}_{str(message.from_user.id)[-2::]}'))
        await bot.send_message(message.chat.id, text='❗️ Чтобы открыть больше введите /education\n'
                                                     '🛠 Список доступных работ 🛠', reply_markup=buttons)


# /leavejob Уволиться
async def leavejob(message):
    await check_user(message)
    user_id = message.from_user.id

    user_info = database.users.find_one({'id': user_id})
    res_info = res_database.job.find_one({'id': user_id})
    # Если нигде не работаю
    if res_info is None:
        await message.answer(f'{await username(message)}, вы нигде не работаете!', parse_mode='HTML')
        return
    # Если работаю, но не в данный момент
    if user_info['job'] != 'нет' and res_info['working'] == False:
        # Если есть бизнес, то нельзя уволиться
        if user_info['job'] == 'Предприниматель':
            # проверка есть ли бизнес уже
            isBus = database.users_bus.find_one({'id': message.from_user.id})
            if isBus is not None:
                await message.answer(
                    f'{await username(message)}, вы обладаете бизнесом, чтобы сменить работу вам нужно продать бизнес!\n'
                    f'💎 {isBus["name"]} {isBus["product"]} 💎\n'
                    f'❗️ Для продажи бизнеса введите /sell_bus',
                    parse_mode='HTML')
                return
        if user_info['job'] == 'Строитель':
            boss = database.builders_work.find_one({'id': message.from_user.id})
            if boss is not None:
                await message.answer(f'{await username(message)}, для начала вам нужно уйти со стройки!\n'
                                     f'❗️ Чтобы уйти - /leave_build',
                                     parse_mode='HTML')
                return
        if user_info['job'] == 'Автосборщик':
            boss = database.autocreater_work.find_one({'id': message.from_user.id})
            if boss is not None:
                await message.answer(f'{await username(message)}, для начала вам нужно уйти с автосборки!\n'
                                     f'❗️ Чтобы уйти - /leave_creater',
                                     parse_mode='HTML')
                return
        # обновленние данных в БД
        database.users.update_one({'id': user_id}, {'$set': {'job': 'нет'}})
        res_database.job.delete_one({'id': user_id})
        await message.answer(f'{await username(message)}, вы уволились!',
                             parse_mode='HTML')
    elif user_info['job'] != 'нет' and res_info['working']:
        # Получение переменных с строки
        tz = pytz.timezone('Etc/GMT-3')
        res_job_info = res_database.job.find_one({'id': user_id})
        date, time = res_job_info['time'].split(' ')
        year, month, day = date.split('-')
        hour, minute, second = time.split(':')
        time_job = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
        time_now = datetime.datetime(datetime.datetime.now(tz=tz).year, datetime.datetime.now(tz=tz).month,
                                     datetime.datetime.now(tz=tz).day, datetime.datetime.now(tz=tz).hour,
                                     datetime.datetime.now(tz=tz).minute, datetime.datetime.now(tz=tz).second)
        result = time_job - time_now

        await bot.send_message(message.chat.id,
                               text=f'{await username(message)}, вам ещё осталось работать {result} мин ',
                               parse_mode='HTML')
    else:
        await message.answer(f'{await username(message)}, вы нигде не работаете!', parse_mode='HTML')


# Окончание работы если не гражданин
async def end_job_no_citizen(message: types.Message, job):
    # Получение данных о машине
    user_id = message.from_user.id
    job_info = database.jobs.find_one({'name_job': job})
    user_info = database.users.find_one({'id': user_id})
    if job == 'Работник мака':
        # обновление данных пользователя
        database.users.update_one({'id': user_id}, {'$set': {'exp': user_info['exp'] + int(job_info['exp_for_job']),
                                                             'cash': user_info['cash'] + int(job_info['cash']),
                                                             'food': user_info['food'] + food_mak}})
        res_database.job.update_one({'id': user_id}, {'$set': {'working': False}})
        await bot.send_message(message.chat.id,
                               f'{await username(message)}, вы окончили работу и получили за это:\n'
                               f'🏵 +{job_info["exp_for_job"]} опыта\n'
                               f'💵 +{job_info["cash"]}$\n'
                               f'🍔 +{food_mak}кг пищи\n', parse_mode='HTML')
    elif job == 'Повар':
        # обновление данных пользователя
        database.users.update_one({'id': user_id}, {'$set': {'exp': user_info['exp'] + int(job_info['exp_for_job']),
                                                             'cash': user_info['cash'] + int(job_info['cash']),
                                                             'food': user_info['food'] + food_povar}})
        res_database.job.update_one({'id': user_id}, {'$set': {'working': False}})
        await bot.send_message(message.chat.id,
                               f'{await username(message)}, вы окончили работу и получили за это:\n'
                               f'🏵 +{job_info["exp_for_job"]} опыта\n'
                               f'💵 +{job_info["cash"]}$\n'
                               f'🍔 +{food_povar}кг пищи\n', parse_mode='HTML')
    elif job == 'Пекарь' or job == 'Кондитер':
        # обновление данных пользователя
        database.users.update_one({'id': user_id}, {'$set': {'exp': user_info['exp'] + int(job_info['exp_for_job']),
                                                             'cash': user_info['cash'] + int(job_info['cash']),
                                                             'food': user_info['food'] + food_pekar}})
        res_database.job.update_one({'id': user_id}, {'$set': {'working': False}})
        await bot.send_message(message.chat.id,
                               f'{await username(message)}, вы окончили работу и получили за это:\n'
                               f'🏵 +{job_info["exp_for_job"]} опыта\n'
                               f'💵 +{job_info["cash"]}$\n'
                               f'🍔 +{food_pekar}кг пищи\n', parse_mode='HTML')
    elif job == 'Фермер':
        # обновленние данных пользователя
        database.users.update_one({'id': user_id}, {'$set': {'exp': user_info['exp'] + int(job_info['exp_for_job']),
                                                             'cash': user_info['cash'] + int(job_info['cash']),
                                                             'food': user_info['food'] + food_fermer}})
        res_database.job.update_one({'id': user_id}, {'$set': {'working': False}})
        await bot.send_message(message.chat.id,
                               f'{await username(message)}, вы окончили работу и получили за это:\n'
                               f'🏵 +{job_info["exp_for_job"]} опыта\n'
                               f'💵 +{job_info["cash"]}$\n'
                               f'🍔 +{food_fermer}кг пищи\n', parse_mode='HTML')
    elif job == 'Нефтяник':
        oil = 50  # Нефть
        # обновленние данных пользователя
        database.users.update_one({'id': user_id}, {'$set': {'exp': user_info['exp'] + int(job_info['exp_for_job']),
                                                             'cash': user_info['cash'] + int(job_info['cash']),
                                                             'oil': user_info['oil'] + oil}})
        res_database.job.update_one({'id': user_id}, {'$set': {'working': False}})
        await bot.send_message(message.chat.id,
                               f'{await username(message)}, вы окончили работу и получили за это:\n'
                               f'🏵 +{job_info["exp_for_job"]} опыта\n'
                               f'💵 +{job_info["cash"]}$\n'
                               f'🖤 +{oil}л\n', parse_mode='HTML')
    else:
        # обновленние данных пользователя
        database.users.update_one({'id': user_id}, {'$set': {'exp': user_info['exp'] + int(job_info['exp_for_job']),
                                                             'cash': user_info['cash'] + int(job_info['cash'])}})
        res_database.job.update_one({'id': user_id}, {'$set': {'working': False}})
        await bot.send_message(message.chat.id,
                               f'{await username(message)}, вы окончили работу и получили за это:\n'
                               f'🏵 +{job_info["exp_for_job"]} опыта\n'
                               f'💵 +{job_info["cash"]}$\n', parse_mode='HTML')


# Окончание работы если гражданин
async def end_job_citizen(message: types.Message, job):
    # Получение данных о машине
    user_id = message.from_user.id

    job_info = database.jobs.find_one({'name_job': job})
    user_info = database.users.find_one({'id': user_id})
    country_info = database.countries.find_one({'country': user_info['citizen_country']})
    if job == 'Автосборщик':
        # получение/обновление данных о бизнесе
        job_info = database.jobs.find_one({'name_job': 'Автосборщик'})

        bus_info = database.users_bus.find_one(
            {'boss': database.autocreater_work.find_one({'creater': user_id})['boss']})
        buss = database.businesses.find_one({'product': bus_info['product']})
        car_info = database.cars.find_one({'name_car': bus_info['product']})
        job_cash = car_info['cost'] * 0.1
        # Если создалась 1 штука
        if bus_info['time_to_create'] <= job_info['job_time']:
            # Обновление времени для создания
            database.users_bus.update_one(
                {'boss': database.autocreater_work.find_one({'creater': user_id})['boss']},
                {'$set': {'time_to_create': buss['time_to_create']}})
            # +1 к количеству
            database.cars.update_one({'name_car': bus_info['product']}, {'$set': {'count': car_info['count'] + 1}})
            arr = next(os.walk(f'{os.getcwd()}/res/cars_pic'))[2]
            autocreater_list = database.autocreater_work.find(
                {'boss': database.autocreater_work.find_one({'creater': user_id})['boss']})
            # Выдача зп предпринимателю
            database.users.update_one({'id': database.autocreater_work.find_one({'creater': user_id})['boss']},
                                      {'$set': {'cash': database.users.find_one(
                                          {'id': database.autocreater_work.find_one({'creater': user_id})['boss']})[
                                                            'cash'] +
                                                        car_info['cost'] * 0.5}})
            for autocreater in autocreater_list:
                # Выдача зп автосборщикам
                autocreater_info = database.users.find_one({'id': autocreater['creater']})
                database.users.update_one({'id': autocreater['creater']},
                                          {'$set': {'cash': autocreater_info['cash'] + round(float(job_cash) - round(
                                              round(float(job_cash)) * (
                                                      country_info['nalog_job'] / 100)))}})
                res_database.job.update_one({'id': autocreater['creater']}, {'$set': {'working': False}})
                # обновление данных страны
                database.countries.update_one({'country': autocreater_info['citizen_country']}, {
                    '$set': {'cash': country_info['cash'] + round(
                        round(float(job_cash)) * (country_info['nalog_job'] / 100))}})
                await bot.send_message(autocreater_info['id'],
                                       f'{await username(message)}, ваше предприятие произвело 1 единицу продукции!\n'
                                       f'💵 +{autocreater_info["cash"] - round(round(float(job_cash)) * (country_info["nalog_job"] / 100))}$\n'
                                       f'Государству:\n'
                                       f'💵 +{round(round(float(job_cash)) * (country_info["nalog_job"] / 100))}',
                                       parse_mode='HTML')
            for car in arr:
                if bus_info['product'] in car:
                    await bot.send_photo(message.chat.id, photo=InputFile(f'{os.getcwd()}/res/cars_pic/{car}'),
                                         caption=f'Была произведена {bus_info["product"]}\n'
                                                 f'Текущее количество в мире: {car_info["count"] + 1}')

        else:
            # Обновление оставшегося времени для создания
            database.users_bus.update_one(
                {'boss': database.autocreater_work.find_one({'creater': user_id})['boss']},
                {'$set': {'time_to_create': bus_info['time_to_create'] - job_info['job_time']}})
        database.users.update_one({'id': message.from_user.id},
                                  {'$set': {'exp': user_info['exp'] + int(job_info['exp_for_job']), }})
        await bot.send_message(message.chat.id,
                               f'{await username(message)}, вы окончили работу и получили за это:\n'
                               f'🏵 +{job_info["exp_for_job"]} опыта\n',
                               parse_mode='HTML')




    elif job == 'Работник мака':
        # обновление данных пользователя
        database.users.update_one({'id': user_id}, {'$set': {'exp': user_info['exp'] + int(job_info['exp_for_job']),
                                                             'cash': user_info['cash'] + int(job_info['cash'] - round(
                                                                 int(job_info['cash']) * (
                                                                         country_info['nalog_job'] / 100))),
                                                             'food': user_info['food'] + round(food_mak * 0.1)}})
        res_database.job.update_one({'id': user_id}, {'$set': {'working': False}})

        # обновление данных страны
        database.countries.update_one({'country': user_info['citizen_country']}, {
            '$set': {'cash': country_info['cash'] + round(int(job_info['cash']) * (country_info['nalog_job'] / 100)),
                     'food': int(country_info['food']) + food_mak}})
        await bot.send_message(message.chat.id,
                               f'{await username(message)}, вы окончили работу и получили за это:\n'
                               f'🏵 +{job_info["exp_for_job"]} опыта\n'
                               f'💵 +{job_info["cash"] - round(int(job_info["cash"]) * (country_info["nalog_job"] / 100))}$\n'
                               f'🍔 +{round(food_mak * 0.1)}кг пищи\n'
                               f'Государству:\n'
                               f'🍔 +{food_mak}кг пищи\n'
                               f'💵 +{round(int(job_info["cash"] * (country_info["nalog_job"] / 100)))}',
                               parse_mode='HTML')
    elif job == 'Повар':
        # обновление данных пользователя
        database.users.update_one({'id': user_id}, {'$set': {'exp': user_info['exp'] + int(job_info['exp_for_job']),
                                                             'cash': user_info['cash'] + int(job_info['cash'] - round(
                                                                 int(job_info['cash']) * (
                                                                         country_info['nalog_job'] / 100))),
                                                             'food': user_info['food'] + round(food_povar * 0.1)}})
        res_database.job.update_one({'id': user_id}, {'$set': {'working': False}})

        # обновление данных страны
        database.countries.update_one({'country': user_info['citizen_country']}, {
            '$set': {'cash': country_info['cash'] + round(int(job_info['cash']) * (country_info['nalog_job'] / 100)),
                     'food': int(country_info['food']) + food_povar}})
        await bot.send_message(message.chat.id,
                               f'{await username(message)}, вы окончили работу и получили за это:\n'
                               f'🏵 +{job_info["exp_for_job"]} опыта\n'
                               f'💵 +{job_info["cash"] - round(int(job_info["cash"]) * (country_info["nalog_job"] / 100))}$\n'
                               f'🍔 +{round(food_povar * 0.1)}кг пищи\n'
                               f'Государству:\n'
                               f'🍔 +{food_povar}кг пищи\n'
                               f'💵 +{round(int(job_info["cash"] * (country_info["nalog_job"] / 100)))}',
                               parse_mode='HTML')
    elif job == 'Пекарь' or job == 'Кондитер':
        # обновление данных пользователя
        database.users.update_one({'id': user_id}, {'$set': {'exp': user_info['exp'] + int(job_info['exp_for_job']),
                                                             'cash': user_info['cash'] + int(job_info['cash'] - round(
                                                                 int(job_info['cash']) * (
                                                                         country_info['nalog_job'] / 100))),
                                                             'food': user_info['food'] + round(food_pekar * 0.1)}})
        res_database.job.update_one({'id': user_id}, {'$set': {'working': False}})

        # обновление данных страны
        database.countries.update_one({'country': user_info['citizen_country']}, {
            '$set': {'cash': country_info['cash'] + round(int(job_info['cash']) * (country_info['nalog_job'] / 100)),
                     'food': int(country_info['food']) + food_pekar}})
        await bot.send_message(message.chat.id,
                               f'{await username(message)}, вы окончили работу и получили за это:\n'
                               f'🏵 +{job_info["exp_for_job"]} опыта\n'
                               f'💵 +{job_info["cash"] - round(int(job_info["cash"]) * (country_info["nalog_job"] / 100))}$\n'
                               f'🍔 +{round(food_pekar * 0.1)}кг пищи\n'
                               f'Государству:\n'
                               f'🍔 +{food_pekar}кг пищи\n'
                               f'💵 +{round(int(job_info["cash"] * (country_info["nalog_job"] / 100)))}',
                               parse_mode='HTML')
    elif job == 'Фермер':
        # обновление данных пользователя
        database.users.update_one({'id': user_id}, {'$set': {'exp': user_info['exp'] + int(job_info['exp_for_job']),
                                                             'cash': user_info['cash'] + int(job_info['cash'] - round(
                                                                 int(job_info['cash']) * (
                                                                         country_info['nalog_job'] / 100))),
                                                             'food': user_info['food'] + round(food_fermer * 0.1)}})
        res_database.job.update_one({'id': user_id}, {'$set': {'working': False}})

        # обновление данных страны
        database.countries.update_one({'country': user_info['citizen_country']}, {
            '$set': {'cash': country_info['cash'] + round(int(job_info['cash']) * (country_info['nalog_job'] / 100)),
                     'food': int(country_info['food']) + food_fermer}})
        await bot.send_message(message.chat.id,
                               f'{await username(message)}, вы окончили работу и получили за это:\n'
                               f'🏵 +{job_info["exp_for_job"]} опыта\n'
                               f'💵 +{job_info["cash"] - round(int(job_info["cash"]) * (country_info["nalog_job"] / 100))}$\n'
                               f'🍔 +{round(food_fermer * 0.1)}кг пищи\n'
                               f'Государству:\n'
                               f'🍔 +{food_fermer}кг пищи\n'
                               f'💵 +{round(int(job_info["cash"] * (country_info["nalog_job"] / 100)))}',
                               parse_mode='HTML')
    elif job == 'Нефтяник':
        oil = 50  # Нефть
        # обновление данных пользователя
        database.users.update_one({'id': user_id}, {'$set': {'exp': user_info['exp'] + int(job_info['exp_for_job']),
                                                             'cash': user_info['cash'] + int(job_info['cash'] - round(
                                                                 int(job_info['cash']) * (
                                                                         country_info['nalog_job'] / 100))),
                                                             'oil': user_info['oil'] + round(oil * 0.1)}})
        res_database.job.update_one({'id': user_id}, {'$set': {'working': False}})

        # обновление данных страны
        database.countries.update_one({'country': user_info['citizen_country']}, {
            '$set': {'cash': country_info['cash'] + round(int(job_info['cash']) * (country_info['nalog_job'] / 100)),
                     'oil': int(country_info['oil']) + oil}})
        await bot.send_message(message.chat.id,
                               f'{await username(message)}, вы окончили работу и получили за это:\n'
                               f'🏵 +{job_info["exp_for_job"]} опыта\n'
                               f'💵 +{job_info["cash"] - round(int(job_info["cash"]) * (country_info["nalog_job"] / 100))}$\n'
                               f'🖤 +{round(oil * 0.1)}л\n'
                               f'Государству:\n'
                               f'🖤 +{oil}л\n'
                               f'💵 +{round(int(job_info["cash"] * (country_info["nalog_job"] / 100)))}',
                               parse_mode='HTML')
    else:
        # обновление данных пользователя
        database.users.update_one({'id': user_id}, {'$set': {'exp': user_info['exp'] + int(job_info['exp_for_job']),
                                                             'cash': user_info['cash'] + int(job_info['cash'] - round(
                                                                 int(job_info['cash']) * (
                                                                         country_info['nalog_job'] / 100)))}})
        res_database.job.update_one({'id': user_id}, {'$set': {'working': False}})

        # обновление данных страны
        database.countries.update_one({'country': user_info['citizen_country']}, {
            '$set': {'cash': country_info['cash'] + round(int(job_info['cash']) * (country_info['nalog_job'] / 100))}})
        await bot.send_message(message.chat.id,
                               f'{await username(message)}, вы окончили работу и получили за это:\n'
                               f'🏵 +{job_info["exp_for_job"]} опыта\n'
                               f'💵 +{job_info["cash"] - round(int(job_info["cash"]) * (country_info["nalog_job"] / 100))}$\n'
                               f'Государству:\n'
                               f'💵 +{round(int(job_info["cash"] * (country_info["nalog_job"] / 100)))}',
                               parse_mode='HTML')


# Окончание болезни
async def end_disease(message: types.Message):
    user_id = message.from_user.id
    res_database.disease.delete_one({'id': user_id})
    await bot.send_message(message.chat.id, f'{await username(message)}, вы выздоровили!', parse_mode='HTML')


# Проверка больше ли еды в стране
async def check_food_country(user_id):
    country_info = database.countries.find_one({'president'})
    president_info = database.users.find_one({'president'})
    if country_info['food'] < 50:
        database.users.update_one({'id': country_info['president']}, {'$set': {'president_country': 'нет'}})
        users_info = database.users.find({'citizen_country': country_info['country']})
        for user in users_info:
            database.users.update_one({'id': user['id']}, {'$set': {'citizen_country': 'нет'}})
        country = res_database.countries.find_one({'country': president_info['president_country']})
        database.countries.update_one({
            'country': country['country'],
            'president': 0,
            'cash': int(country['cash']),
            'oil': int(country['oil']),
            'food': int(country['food']),
            'territory': int(country['territory']),
            'level': 0,
            'max_people': int(country['max_people']),
            'terr_for_farmers': int(country['terr_for_farmers']),
            'cost': int(country['cost']),
            'nalog_job': 1
        })
        res_database.country_check_food.delete_one({'id': user_id})
        await bot.send_message(country_info['president'],
                               f'{username_2(country_info["president"], president_info["firstname"])}, вы не восстановили еду, поэтому ваша страна {country_info["country"]} была расформирована и возврату не подлежит!',
                               parse_mode='HTML')


def register_handlers_countries(dp: Dispatcher):
    dp.register_message_handler(work, content_types='text',
                                text=['/work', 'работа', 'работать', 'Работа', 'Работать', 'робота', 'Робота'])
    dp.register_message_handler(getjob, content_types='text',
                                text=['работы', 'Работы', '/jobs', 'Устроиться на работу', 'устроиться на работу'])
    dp.register_message_handler(leavejob, content_types='text',
                                text=['Уволиться', 'уволиться', '/leavejob', 'уволится', 'Уволится',
                                      'Уволится с работы', 'уволится с работы', 'Уволиться с работы',
                                      'уволиться с работы'])
