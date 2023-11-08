import asyncio
import datetime
import json
import logging
import math
import os
import random
from datetime import datetime, timedelta
from time import perf_counter
from site_flask import keep_alive

import pytz
from PIL import Image, ImageDraw, ImageFont, ImageOps
from aiogram import executor, types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import InputFile
from aiogram.utils.markdown import hlink
from aiogram.utils.markdown import quote_html
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dateutil import parser

from create_bot import bot
from create_bot import dp
from filters import antiflood
from filters.filters import IsPromo, ShareMoney

# from background import keep_alive

from pymongo.mongo_client import MongoClient

# БД
database = MongoClient(
    "mongodb+srv://maksemqwerty:maksem228@cluster0.mylnsur.mongodb.net/?retryWrites=true&w=majority").data

res_database = MongoClient(
    "mongodb+srv://maksemqwerty:maksem228@cluster0.mylnsur.mongodb.net/?retryWrites=true&w=majority").res

food_mak = 20
food_povar = 45
food_pekar = 35
food_fermer = 100


# Чтобы не слетали импорты
def imports():
    print(pytz)
    print(datetime)
    print(asyncio)
    print(parser)
    print(random)
    print(math)
    print(json)
    print(Dispatcher)
    print(AsyncIOScheduler)


# Разбиение на триады
#import locale

#locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")
#  Логгирование
logging.basicConfig(filename='app/logs.log', filemode='w', level=logging.INFO)

@dp.message_handler(commands=['logs'])
async def send_logs(message: types.message):
    devs_id = [735569411, 1578668223]
    user_id = message.from_user.id
    if user_id in devs_id:
        await message.reply_document(open('app/logs.log', 'rb'))
    else:
        await message.reply('Облом =)')
        

@dp.message_handler(commands=['jobs_info'])
async def jobs_info(message: types.Message):
    users_id = [735569411, 1578668223, 5325181616]
    user_id = message.from_user.id
    if user_id in users_id:    
        data = database.jobs.find()
        for item in data:
            msg = f"Название работы: {item['name_job']}\n    Требуется опыта для работы: {item['need_exp']}\n    Зарплата: {item['cash']}\n    Время работы: {item['job_time']}мин\n    Снимаемая еда за работу: {item['need_food']}\n    Стоимость обучения: {item['need_cash']}"
            await message.reply(msg)
    else:
        await message.reply('Данная команда предназначена только для разработчиков и менеджеров бота')


# Вызывается при старте
async def on_startup(_):

    # проверка активности президентов
    tz = pytz.timezone('Etc/GMT-3')
    scheduler.add_job(check_president, "cron",
                      hour=6, timezone=tz)
    # бэкап в 8 утра
    scheduler.add_job(backup, "cron",
                      hour=8, timezone=tz)
    # бэкап в 8 вечера
    scheduler.add_job(backup, "cron",
                      hour=16, timezone=tz)

    data_vuz = list(res_database.vuz.find())
    for info_vuz in data_vuz:
        # Получение переменных с строки
        tz = pytz.timezone('Etc/GMT-3')
        date, time = info_vuz['time'].split(' ')
        year, month, day = date.split('-')
        hour, minute, second = time.split(':')
        time_vuz = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
        time_now = datetime(datetime.now(tz=tz).year, datetime.now(tz=tz).month,
                            datetime.now(tz=tz).day, datetime.now(tz=tz).hour,
                            datetime.now(tz=tz).minute, datetime.now(tz=tz).second)
        result = time_vuz - time_now
        # Если уже окончил
        educ_info = database.education.find_one({'id': info_vuz["id"]})
        if '-' in str(result):
            user_info = database.users.find_one({'id': info_vuz["id"]})
            job_list = [i for i in educ_info['jobs'].split(' ')]
            job_list.append(str(educ_info["ucheb"]).replace('ВУЗ', '').strip())
            # обновление данных в БД
            database.education.update_one({'id': info_vuz["id"]}, {'$set': {'ucheb': 'нет',
                                                                            'jobs': ' '.join(job_list)}})
            res_database.vuz.delete_one({'id': info_vuz["id"]})
            await bot.send_message(info_vuz["id"],
                                   f'{await username_2(info_vuz["id"], user_info["firstname"])}, вы окончили обучение в ВУЗе "{str(educ_info["ucheb"]).replace("ВУЗ", "").strip()}"\n'
                                   f'Теперь вам доступна профессия {str(educ_info["ucheb"]).replace("ВУЗ", "").strip()}',
                                   parse_mode='HTML')
        else:
            scheduler.add_job(start_vuz, trigger="date", run_date=info_vuz["time"], timezone=tz,
                              id=f'{info_vuz["id"]}_vuz',
                              args=(info_vuz["id"], str(educ_info["ucheb"]).replace("ВУЗ", "").strip()))
    data_job = list(res_database.job.find({'working': True}))
    for info_job in data_job:
        try:
            # Получение переменных с строки
            tz = pytz.timezone('Etc/GMT-3')

            date, time = info_job['time'].split(' ')
            year, month, day = date.split('-')
            hour, minute, second = time.split(':')
            time_vuz = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
            time_now = datetime(datetime.now(tz=tz).year, datetime.now(tz=tz).month,
                                datetime.now(tz=tz).day, datetime.now(tz=tz).hour,
                                datetime.now(tz=tz).minute, datetime.now(tz=tz).second)
            result = time_vuz - time_now
            # Если уже окончил

            if '-' in str(result):
                citizen = database.users.find_one({'id': info_job['id']})['citizen_country']
                # Если гражданин
                if citizen != 'нет':
                    await end_job_citizen(info_job['id'], info_job['id'])
                else:
                    await end_job_no_citizen(info_job['id'], info_job['id'])
            else:
                citizen = database.users.find_one({'id': info_job['id']})['citizen_country']
                # Если гражданин
                if citizen != 'нет':
                    scheduler.add_job(end_job_citizen, "date",
                                      run_date=info_job['time'],
                                      args=(info_job['id'], info_job['id']), id=str(info_job['id']), timezone=tz)
                else:
                    scheduler.add_job(end_job_no_citizen, "date",
                                      run_date=info_job['time'],
                                      args=(info_job['id'], info_job['id']), id=str(info_job['id']), timezone=tz)
        except:
            pass
    data_disease = list(res_database.disease.find({'disease': True}))
    for info_disease in data_disease:
        try:
            # Получение переменных с строки
            tz = pytz.timezone('Etc/GMT-3')

            date, time = info_disease['time'].split(' ')
            year, month, day = date.split('-')
            hour, minute, second = time.split(':')
            time_vuz = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
            time_now = datetime(datetime.now(tz=tz).year, datetime.now(tz=tz).month,
                                datetime.now(tz=tz).day, datetime.now(tz=tz).hour,
                                datetime.now(tz=tz).minute, datetime.now(tz=tz).second)
            result = time_vuz - time_now
            # Если уже окончил

            if '-' in str(result):
                await end_disease(info_disease['id'])
            else:
                scheduler.add_job(end_disease, "date",
                                  run_date=info_disease['time'],
                                  args=(info_disease['id'],), timezone=tz)
        except:
            pass

    # Стройка бизнеса
    build_data = list(res_database.build_bus.find())
    for build in build_data:
        try:
            # Получение переменных с строки
            tz = pytz.timezone('Etc/GMT-3')

            date, time = build['time'].split(' ')
            year, month, day = date.split('-')
            hour, minute, second = time.split(':')
            time_vuz = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
            time_now = datetime(datetime.now(tz=tz).year, datetime.now(tz=tz).month,
                                datetime.now(tz=tz).day, datetime.now(tz=tz).hour,
                                datetime.now(tz=tz).minute, datetime.now(tz=tz).second)
            result = time_vuz - time_now
            # Если уже окончил

            if '-' in str(result):
                await end_build_bus(build['boss'])
            else:
                scheduler.add_job(end_build_bus, "date",
                                  run_date=build['time'],
                                  args=(build['boss'],), id=f'{build["boss"]}_build', timezone=tz)
        except:
            pass

    check_food_countr = list(res_database.country_check_food.find())
    for check_food in check_food_countr:
        # Получение переменных с строки
        tz = pytz.timezone('Etc/GMT-3')

        date, time = check_food['time'].split(' ')
        year, month, day = date.split('-')
        hour, minute, second = time.split(':')
        time_vuz = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
        time_now = datetime(datetime.now(tz=tz).year, datetime.now(tz=tz).month,
                            datetime.now(tz=tz).day, datetime.now(tz=tz).hour,
                            datetime.now(tz=tz).minute, datetime.now(tz=tz).second)
        result = time_vuz - time_now
        # Если вышло время
        if '-' in str(result):
            await check_food_country(check_food['id'])
        else:
            scheduler.add_job(check_food_country, "date",
                              run_date=check_food['time'],
                              args=(check_food['id'],), timezone=tz)

    autoschool_list = list(res_database.autoschool.find())
    for autoschool_info in autoschool_list:
        # Получение переменных с строки
        tz = pytz.timezone('Etc/GMT-3')
        date, time = autoschool_info['time'].split(' ')
        year, month, day = date.split('-')
        hour, minute, second = time.split(':')
        time_job = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
        time_now = datetime(datetime.now(tz=tz).year, datetime.now(tz=tz).month,
                            datetime.now(tz=tz).day, datetime.now(tz=tz).hour,
                            datetime.now(tz=tz).minute, datetime.now(tz=tz).second)
        result = time_job - time_now
        # Если уже отработал
        if '-' in str(result):
            await end_autoschool(autoschool_info['id'])
        else:
            scheduler.add_job(end_autoschool, "date",
                              run_date=autoschool_info['time'],
                              args=(autoschool_info['id'],), timezone=tz)

    # Проверка есть ли все страны в БД
    countries_db = database.countries.find()
    list_countries = []
    for i in countries_db:
        list_countries.append(i['country'])
    countries_res = res_database.countries.find()
    for country in countries_res:
        if country['country'] not in list_countries:
            database.countries.insert_one({
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
    print('БОТ ЕБАШИТ')


# Проверка больше ли еды в стране
async def check_food_country(user_id):
    country_info = database.countries.find_one({'president': user_id})
    # Если нет страны у президента
    if country_info is None:
        res_database.country_check_food.delete_one({'id': user_id})
        return
    president_info = database.users.find_one({'president': user_id})
    if country_info['food'] < 50:
        database.users.update_one({'id': country_info['president']}, {'$set': {'president_country': 'нет'}})
        users_info = database.users.find({'citizen_country': country_info['country']})
        for user in users_info:
            database.users.update_one({'id': user['id']}, {'$set': {'citizen_country': 'нет'}})
        country = res_database.countries.find_one({'country': president_info['president_country']})
        database.countries.update_one({'country': country['country']}, {'$set': {
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
        }})
        res_database.country_check_food.delete_one({'id': user_id})
        await bot.send_message(country_info['president'],
                               f'{username_2(country_info["president"], president_info["firstname"])}, вы не восстановили еду, поэтому ваша страна {country_info["country"]} была расформирована и возврату не подлежит!',
                               parse_mode='HTML')
    else:
        res_database.country_check_food.delete_one({'id': user_id})

# Проверка автошколы
async def end_autoschool(user_id):
    database.education.update_one({'id': user_id}, {'$set': {'auto_school': 'да'}})
    user_info = database.users.find_one({"id": user_id})
    res_database.autoschool.delete_one({'id': user_id})
    await bot.send_message(user_id, f'{await username_2(user_id, user_info["firstname"])}, вы окончили обучение на B категорию!', parse_mode='HTML')

# Окончание стройки объекта
async def end_build_bus(user_id):
    boss_info = database.users.find_one({'id': user_id})
    builders_info = list(database.builders_work.find({'boss': user_id}))
    bus_info = database.users_bus.find_one({'boss': user_id})
    # Изменение статуса стройки
    database.users_bus.update_one({'boss': user_id}, {'$set': {'status': 'work'}})
    # Выдача денег строителям\расформирование их
    for builder in builders_info:
        builder_info = database.users.find_one({'id': builder['builder']})
        job_info = database.jobs.find_one({'name_job': builder_info['job']})
        database.users.update_one({'id': builders_info['builder']},
                                  {'$set': {'cash': builder_info['cash'] + bus_info['cost'] * bus_info['bpay'],
                                            'exp': builder_info['exp'] + job_info['exp_for_job']}})
        database.builders_work.delete_one({'builder': builder['builder']})
        await bot.send_message(builder['builder'],
                               f'{await username_2(builder_info["id"], builders_info["firstname"])}, вы получили вознаграждение за стройку объекта {bus_info["name"]} {bus_info["product"]}\n'
                               f'💵 +{bus_info["bpay"]}\n'
                               f'🏵 +{job_info["exp_for_job"]}', parse_mode='HTML')
    res_database.build_bus.delete_one({'boss': user_id})
    await bot.send_message(user_id,
                           f'{await username_2(user_id, boss_info["firstname"])}, ваш бизнес {bus_info["name"]} {bus_info["product"]} завершил стройку!',
                           parse_mode='HTML')


# Окончание работы если не гражданин
async def end_job_no_citizen(user_id, chat_id):
    try:

        # Получение данных о машине
        user_info = database.users.find_one({'id': user_id})
        job_info = database.jobs.find_one({'name_job': user_info['job']})
        if user_info['job'] == 'Работник мака':
            # обновление данных пользователя
            database.users.update_one({'id': user_id}, {'$set': {'exp': user_info['exp'] + int(job_info['exp_for_job']),
                                                                 'cash': user_info['cash'] + int(job_info['cash']),
                                                                 'food': user_info['food'] + food_mak}})
            res_database.job.update_one({'id': user_id}, {'$set': {'working': False}})
            await bot.send_message(chat_id,
                                   f'{await username_2(user_id, user_info["firstname"])}, вы окончили работу и получили за это:\n'
                                   f'🏵 +{job_info["exp_for_job"]} опыта\n'
                                   f'💵 +{job_info["cash"]}$\n'
                                   f'🍔 +{food_mak}кг пищи\n', parse_mode='HTML')
        elif user_info['job'] == 'Повар':
            # обновление данных пользователя
            database.users.update_one({'id': user_id}, {'$set': {'exp': user_info['exp'] + int(job_info['exp_for_job']),
                                                                 'cash': user_info['cash'] + int(job_info['cash']),
                                                                 'food': user_info['food'] + food_povar}})
            res_database.job.update_one({'id': user_id}, {'$set': {'working': False}})
            await bot.send_message(chat_id,
                                   f'{await username_2(user_id, user_info["firstname"])}, вы окончили работу и получили за это:\n'
                                   f'🏵 +{job_info["exp_for_job"]} опыта\n'
                                   f'💵 +{job_info["cash"]}$\n'
                                   f'🍔 +{food_povar}кг пищи\n', parse_mode='HTML')
        elif user_info['job'] == 'Пекарь' or user_info['job'] == 'Кондитер':
            # обновление данных пользователя
            database.users.update_one({'id': user_id}, {'$set': {'exp': user_info['exp'] + int(job_info['exp_for_job']),
                                                                 'cash': user_info['cash'] + int(job_info['cash']),
                                                                 'food': user_info['food'] + food_pekar}})
            res_database.job.update_one({'id': user_id}, {'$set': {'working': False}})
            await bot.send_message(chat_id,
                                   f'{await username_2(user_id, user_info["firstname"])}, вы окончили работу и получили за это:\n'
                                   f'🏵 +{job_info["exp_for_job"]} опыта\n'
                                   f'💵 +{job_info["cash"]}$\n'
                                   f'🍔 +{food_pekar}кг пищи\n', parse_mode='HTML')
        elif user_info['job'] == 'Фермер':
            # обновленние данных пользователя
            database.users.update_one({'id': user_id}, {'$set': {'exp': user_info['exp'] + int(job_info['exp_for_job']),
                                                                 'cash': user_info['cash'] + int(job_info['cash']),
                                                                 'food': user_info['food'] + food_fermer}})
            res_database.job.update_one({'id': user_id}, {'$set': {'working': False}})
            await bot.send_message(chat_id,
                                   f'{await username_2(user_id, user_info["firstname"])}, вы окончили работу и получили за это:\n'
                                   f'🏵 +{job_info["exp_for_job"]} опыта\n'
                                   f'💵 +{job_info["cash"]}$\n'
                                   f'🍔 +{food_fermer}кг пищи\n', parse_mode='HTML')
        elif user_info['job'] == 'Нефтяник':
            oil = 50  # Нефть
            # обновленние данных пользователя
            database.users.update_one({'id': user_id}, {'$set': {'exp': user_info['exp'] + int(job_info['exp_for_job']),
                                                                 'cash': user_info['cash'] + int(job_info['cash']),
                                                                 'oil': user_info['oil'] + oil}})
            res_database.job.update_one({'id': user_id}, {'$set': {'working': False}})
            await bot.send_message(chat_id,
                                   f'{await username_2(user_id, user_info["firstname"])}, вы окончили работу и получили за это:\n'
                                   f'🏵 +{job_info["exp_for_job"]} опыта\n'
                                   f'💵 +{job_info["cash"]}$\n'
                                   f'🖤 +{oil}л\n', parse_mode='HTML')
        elif user_info['job'] == 'нет':

            res_database.job.delete_one({'id': user_id})
        else:
            # обновленние данных пользователя
            database.users.update_one({'id': user_id}, {'$set': {'exp': user_info['exp'] + int(job_info['exp_for_job']),
                                                                 'cash': user_info['cash'] + int(job_info['cash'])}})
            res_database.job.update_one({'id': user_id}, {'$set': {'working': False}})
            await bot.send_message(chat_id,
                                   f'{await username_2(user_id, user_info["firstname"])}, вы окончили работу и получили за это:\n'
                                   f'🏵 +{job_info["exp_for_job"]} опыта\n'
                                   f'💵 +{job_info["cash"]}$\n', parse_mode='HTML')
    except:
        pass


# Окончание работы если гражданин
async def end_job_citizen(user_id, chat_id):
    # Получение данных
    user_info = database.users.find_one({'id': user_id})
    job_info = database.jobs.find_one({'name_job': user_info['job']})
    country_info = database.countries.find_one({'country': user_info['citizen_country']})
    if user_info['job'] == 'Автосборщик':
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
                                       f'{await username_2(user_id, user_info["firstname"])}, ваше предприятие произвело 1 единицу продукции!\n'
                                       f'💵 +{autocreater_info["cash"] - round(round(float(job_cash)) * (country_info["nalog_job"] / 100))}$\n'
                                       f'Государству:\n'
                                       f'💵 +{round(round(float(job_cash)) * (country_info["nalog_job"] / 100))}',
                                       parse_mode='HTML')
            for car in arr:
                if bus_info['product'] in car:
                    await bot.send_photo(chat_id, photo=InputFile(f'{os.getcwd()}/res/cars_pic/{car}'),
                                         caption=f'Была произведена {bus_info["product"]}\n'
                                                 f'Текущее количество в мире: {car_info["count"] + 1}')

        else:
            # Обновление оставшегося времени для создания
            database.users_bus.update_one(
                {'boss': database.autocreater_work.find_one({'creater': user_id})['boss']},
                {'$set': {'time_to_create': bus_info['time_to_create'] - job_info['job_time']}})
        database.users.update_one({'id': user_id},
                                  {'$set': {'exp': user_info['exp'] + int(job_info['exp_for_job']), }})
        await bot.send_message(chat_id,
                               f'{await username_2(user_id, user_info["firstname"])}, вы окончили работу и получили за это:\n'
                               f'🏵 +{job_info["exp_for_job"]} опыта\n',
                               parse_mode='HTML')
    if user_info['job'] == 'Работник мака':
        # обновление данных пользователя
        database.users.update_one({'id': user_id}, {'$set': {'exp': user_info['exp'] + int(job_info['exp_for_job']),
                                                             'cash': user_info['cash'] + int(
                                                                 job_info['cash'] - round(
                                                                     int(job_info['cash']) * (
                                                                             country_info['nalog_job'] / 100))),
                                                             'food': user_info['food'] + (food_mak - round(
                                                                 int(food_mak) * (country_info["nalog_job"] / 100)))}})
        res_database.job.update_one({'id': user_id}, {'$set': {'working': False}})

        # обновление данных страны
        database.countries.update_one({'country': user_info['citizen_country']}, {
            '$set': {
                'cash': country_info['cash'] + round(int(job_info['cash']) * (country_info['nalog_job'] / 100)),
                'food': int(country_info['food']) + round(int(food_mak * (country_info["nalog_job"] / 100)))}})
        await bot.send_message(chat_id,
                               f'{await username_2(user_id, user_info["firstname"])}, вы окончили работу и получили за это:\n'
                               f'🏵 +{job_info["exp_for_job"]} опыта\n'
                               f'💵 +{job_info["cash"] - round(int(job_info["cash"]) * (country_info["nalog_job"] / 100))}$\n'
                               f'🍔 +{food_mak - round(int(food_mak) * (country_info["nalog_job"] / 100))}кг пищи\n'
                               f'Государству:\n'
                               f'🍔 +{round(int(food_mak * (country_info["nalog_job"] / 100)))}кг пищи\n'
                               f'💵 +{round(int(job_info["cash"] * (country_info["nalog_job"] / 100)))}',
                               parse_mode='HTML')
    elif user_info['job'] == 'Повар':
        # обновление данных пользователя
        database.users.update_one({'id': user_id}, {'$set': {'exp': user_info['exp'] + int(job_info['exp_for_job']),
                                                             'cash': user_info['cash'] + int(
                                                                 job_info['cash'] - round(
                                                                     int(job_info['cash']) * (
                                                                             country_info['nalog_job'] / 100))),
                                                             'food': user_info['food'] + (food_povar - round(
                                                                 int(food_povar) * (
                                                                         country_info["nalog_job"] / 100)))}})
        res_database.job.update_one({'id': user_id}, {'$set': {'working': False}})

        # обновление данных страны
        database.countries.update_one({'country': user_info['citizen_country']}, {
            '$set': {
                'cash': country_info['cash'] + round(int(job_info['cash']) * (country_info['nalog_job'] / 100)),
                'food': int(country_info['food']) + round(int(food_povar * (country_info["nalog_job"] / 100)))}})
        await bot.send_message(chat_id,
                               f'{await username_2(user_id, user_info["firstname"])}, вы окончили работу и получили за это:\n'
                               f'🏵 +{job_info["exp_for_job"]} опыта\n'
                               f'💵 +{job_info["cash"] - round(int(job_info["cash"]) * (country_info["nalog_job"] / 100))}$\n'
                               f'🍔 +{food_povar - round(int(food_povar) * (country_info["nalog_job"] / 100))}кг пищи\n'
                               f'Государству:\n'
                               f'🍔 +{round(int(food_povar * (country_info["nalog_job"] / 100)))}кг пищи\n'
                               f'💵 +{round(int(job_info["cash"] * (country_info["nalog_job"] / 100)))}',
                               parse_mode='HTML')
    elif user_info['job'] == 'Пекарь' or user_info['job'] == 'Кондитер':
        # обновление данных пользователя
        database.users.update_one({'id': user_id}, {'$set': {'exp': user_info['exp'] + int(job_info['exp_for_job']),
                                                             'cash': user_info['cash'] + int(
                                                                 job_info['cash'] - round(
                                                                     int(job_info['cash']) * (
                                                                             country_info['nalog_job'] / 100))),
                                                             'food': user_info['food'] + (food_pekar - round(
                                                                 int(food_pekar) * (
                                                                         country_info["nalog_job"] / 100)))}})
        res_database.job.update_one({'id': user_id}, {'$set': {'working': False}})

        # обновление данных страны
        database.countries.update_one({'country': user_info['citizen_country']}, {
            '$set': {
                'cash': country_info['cash'] + round(int(job_info['cash']) * (country_info['nalog_job'] / 100)),
                'food': int(country_info['food']) + int(food_pekar * (country_info["nalog_job"] / 100))}})
        await bot.send_message(chat_id,
                               f'{await username_2(user_id, user_info["firstname"])}, вы окончили работу и получили за это:\n'
                               f'🏵 +{job_info["exp_for_job"]} опыта\n'
                               f'💵 +{job_info["cash"] - round(int(job_info["cash"]) * (country_info["nalog_job"] / 100))}$\n'
                               f'🍔 +{food_pekar - round(int(food_pekar) * (country_info["nalog_job"] / 100))}кг пищи\n'
                               f'Государству:\n'
                               f'🍔 +{round(int(food_pekar * (country_info["nalog_job"] / 100)))}кг пищи\n'
                               f'💵 +{round(int(job_info["cash"] * (country_info["nalog_job"] / 100)))}',
                               parse_mode='HTML')
    elif user_info['job'] == 'Фермер':
        # обновление данных пользователя
        database.users.update_one({'id': user_id}, {'$set': {'exp': user_info['exp'] + int(job_info['exp_for_job']),
                                                             'cash': user_info['cash'] + int(
                                                                 job_info['cash'] - round(
                                                                     int(job_info['cash']) * (
                                                                             country_info['nalog_job'] / 100))),
                                                             'food': user_info['food'] + (food_fermer - round(
                                                                 int(food_fermer) * (
                                                                         country_info["nalog_job"] / 100)))}})
        res_database.job.update_one({'id': user_id}, {'$set': {'working': False}})

        # обновление данных страны
        database.countries.update_one({'country': user_info['citizen_country']}, {
            '$set': {
                'cash': country_info['cash'] + round(int(job_info['cash']) * (country_info['nalog_job'] / 100)),
                'food': int(country_info['food']) + round(int(food_fermer * (country_info["nalog_job"] / 100)))}})
        await bot.send_message(chat_id,
                               f'{await username_2(user_id, user_info["firstname"])}, вы окончили работу и получили за это:\n'
                               f'🏵 +{job_info["exp_for_job"]} опыта\n'
                               f'💵 +{job_info["cash"] - round(int(job_info["cash"]) * (country_info["nalog_job"] / 100))}$\n'
                               f'🍔 +{food_fermer - round(int(food_fermer) * (country_info["nalog_job"] / 100))}кг пищи\n'
                               f'Государству:\n'
                               f'🍔 +{round(int(food_fermer * (country_info["nalog_job"] / 100)))}кг пищи\n'
                               f'💵 +{round(int(job_info["cash"] * (country_info["nalog_job"] / 100)))}',
                               parse_mode='HTML')
    elif user_info['job'] == 'Нефтяник':
        oil = 50  # Нефть
        # обновление данных пользователя
        database.users.update_one({'id': user_id}, {'$set': {'exp': user_info['exp'] + int(job_info['exp_for_job']),
                                                             'cash': user_info['cash'] + int(
                                                                 job_info['cash'] - round(
                                                                     int(job_info['cash']) * (
                                                                             country_info['nalog_job'] / 100))),
                                                             'oil': user_info['oil'] + (oil - round(
                                                                 int(oil) * (country_info["nalog_job"] / 100)))}})
        res_database.job.update_one({'id': user_id}, {'$set': {'working': False}})

        # обновление данных страны
        database.countries.update_one({'country': user_info['citizen_country']}, {
            '$set': {
                'cash': country_info['cash'] + round(int(job_info['cash']) * (country_info['nalog_job'] / 100)),
                'oil': int(country_info['oil']) + round(int(oil * (country_info["nalog_job"] / 100)))}})
        await bot.send_message(chat_id,
                               f'{await username_2(user_id, user_info["firstname"])}, вы окончили работу и получили за это:\n'
                               f'🏵 +{job_info["exp_for_job"]} опыта\n'
                               f'💵 +{job_info["cash"] - round(int(job_info["cash"]) * (country_info["nalog_job"] / 100))}$\n'
                               f'🖤 +{oil - round(int(oil) * (country_info["nalog_job"] / 100))}л\n'
                               f'Государству:\n'
                               f'🖤 +{round(int(oil * (country_info["nalog_job"] / 100)))}л\n'
                               f'💵 +{round(int(job_info["cash"] * (country_info["nalog_job"] / 100)))}',
                               parse_mode='HTML')
    elif user_info['job'] == 'нет':
        res_database.job.delete_one({'id': user_id})

    else:
        # обновление данных пользователя
        database.users.update_one({'id': user_id}, {'$set': {'exp': user_info['exp'] + int(job_info['exp_for_job']),
                                                             'cash': user_info['cash'] + int(
                                                                 job_info['cash'] - round(
                                                                     int(job_info['cash']) * (
                                                                             country_info['nalog_job'] / 100)))}})
        res_database.job.update_one({'id': user_id}, {'$set': {'working': False}})

        # обновление данных страны
        database.countries.update_one({'country': user_info['citizen_country']}, {
            '$set': {
                'cash': country_info['cash'] + round(int(job_info['cash']) * (country_info['nalog_job'] / 100))}})
        await bot.send_message(chat_id,
                               f'{await username_2(user_id, user_info["firstname"])}, вы окончили работу и получили за это:\n'
                               f'🏵 +{job_info["exp_for_job"]} опыта\n'
                               f'💵 +{job_info["cash"] - round(int(job_info["cash"]) * (country_info["nalog_job"] / 100))}$\n'
                               f'Государству:\n'
                               f'💵 +{round(int(job_info["cash"] * (country_info["nalog_job"] / 100)))}',
                               parse_mode='HTML')


async def isSubsc(message):
    members = await bot.get_chat_member(chat_id=-1001879290440, user_id=message.from_user.id)
    if members['status'] != 'left':
        return
    else:
        await bot.send_message(message.chat.id,
                               f'{await username(message)}, чтобы получить доступ к команде, вы должны состоять в моем канале @makbotinfo',
                               parse_mode='HTML')

# Окончание болезни
async def end_disease(user_id):
    res_database.disease.delete_one({'id': user_id})
    user_info = database.users.find_one({'id': user_id})
    await bot.send_message(user_id, f'{await username_2(user_id, user_info["firstname"])}, вы выздоровили!', parse_mode='HTML')
class Cong(StatesGroup):
    texta = State()


# /senda Рассылка всем
@dp.message_handler(commands='senda')
async def sendl(message):
    await message.delete()
    await Cong.texta.set()
    await bot.send_message(message.chat.id, f'Введите текст для рассылки')


@dp.message_handler(content_types=['text'], state=Cong.texta)
async def text(message, state: FSMContext):
    txt = message.text
    users = list(database.users.find())
    num = 0
    await state.finish()
    for user in users:
        try:
            await bot.send_message(user['id'], txt)
            num += 1
        except:
            pass
    await message.reply(f'Текст разослан {num} раз')

@dp.message_handler(content_types='tex', text=['Ивент', 'ивент', 'Событие', 'событие'])
async def evets(message: types.Message):
    await message.reply(f'Проходит событие на 1 БП (РУ регион) \n'
                        f'Чтобы быть участником события вам необходимо:\n'
                        f'1. Быть подписанным на @makbotinfo\n'
                        f'2. Состоять в чате @wotblitz_tt\n\n'
                        f'А победитель будет выбран по тикетам - кто больше наберет\n'
                        f'Тикеты можно купить за 1кк по команде /ticket\n'
                        f'Тикет даётся за каждого приведенного друга по вашей ссылке /refer\n'
                        f'Чтобы просмотреть кол-во ваших тикетов /myticket\n\n'
                        f'Конец события: 15.10 в 20.00')

@dp.message_handler(commands='myticket')
async def myticket(message: types.Message):
    event_info = res_database.event.find_one({'id': message.from_user.id})
    if event_info is None:
        await message.reply(f'У вас нет тикетов')
    else:
        await message.reply(f'У вас {event_info["count"]} тикетов')

@dp.message_handler(commands='ticket')
async def ticket(message: types.Message):
    await check_user(message)
    user_info = database.users.find_one({'id': message.from_user.id})
    if user_info['cash'] >= 1_000_000:
        event_info = res_database.event.find_one({'id': message.from_user.id})
        database.users.update_one({'id': message.from_user.id}, {'$set': {'cash': user_info['cash'] - 1_000_000}})
        if event_info is None:
            res_database.event.insert_one({'id': message.from_user.id,
                                           'count': 1})
            await bot.send_message(message.chat.id, f'{await username(message)}, вы приобрели 1 тикет', parse_mode='HTML')
        else:
            res_database.event.update_one({'id': message.from_user.id}, {'$set': {'count': event_info['count'] + 1}})
            await bot.send_message(message.chat.id, f'{await username(message)}, вы приобрели 1 тикет',
                                   parse_mode='HTML')
    else:
        await bot.send_message(message.chat.id, f'{await username(message)}, для покупки тикета вам нужно иметь на балансе 1кк', parse_mode='HTML')

@dp.message_handler(commands='start')
async def start(message: types.Message):
    if message.get_args():
        refer_info = database.users.find_one({'id': message.from_user.id})
        if refer_info is None:
            await check_user(message)
            database.users.update_one({'id': message.from_user.id}, {'$set': {'cash': 2500,
                                                                              'exp': 50}})
            await bot.send_message(message.chat.id, 'Вам были начислены:\n'
                                                    '    - 2500$\n'
                                                    '    - 50 опыта')
            user_info = database.users.find_one({'id': int(message.get_args().split(' ')[0])})
            database.users.update_one({'id': int(message.get_args().split(' ')[0])},
                                      {'$set': {'cash': user_info["cash"] + 5000,
                                                'exp': user_info["exp"] + 100}})
            await bot.send_message(int(message.get_args().split(' ')[0]), 'Вам были начислены за приведенного друга:\n'
                                                                          '    - 5000$\n'
                                                                          '    - 100 опыта\n'
                                                                          '    - 1 тикет')
        event_info = res_database.event.find_one({'id': int(message.get_args().split(' ')[0])})
        if event_info is None:
            res_database.event.insert_one({'id': int(message.get_args().split(' ')[0]),
                                           'count': 1})
        else:
            res_database.event.update_one({'id': int(message.get_args().split(' ')[0])}, {'$set': {'count': event_info['count'] + 1}})

    else:
        await bot.send_message(message.chat.id, f'Привет, я являюсь игровым ботом. Все мои команды по кнопке /help')

# /help Помощь
@dp.message_handler(commands='help')
async def help(message):
    await message.delete()
    await bot.send_message(message.chat.id, f'<a href="https://telegra.ph/Obshchie-komandy-08-18">Общие команды</a>\n'
                                            f'<a href="https://telegra.ph/Modul-Feldsher-08-14">Модуль Фельдшер</a>\n'
                                            f'<a href="https://telegra.ph/Modul-Krupe-08-14">Модуль Крупье</a>\n'
                                            f'<a href="https://telegra.ph/Modul-Avtosborshchik-08-14">Модуль Автосборщик</a>\n'
                                            f'<a href="https://telegra.ph/Modul-Stroitel-08-14">Модуль Строитель</a>\n'
                                            f'<a href="https://telegra.ph/Modul-Predprinimatel-08-14">Модуль Предприниматель</a>\n'
                                            f'<a href="https://telegra.ph/Gppo-08-05">Модуль Образование</a>\n'
                                            f'<a href="https://telegra.ph/Nrr-08-05">Модуль Президент</a>\n\n'
                                            f'Мой канал: @makbotinfo', parse_mode='HTML', disable_web_page_preview=True)


# Игры
@dp.message_handler(commands='games')
async def ginfo(message):
    await check_user(message)
    await bot.send_message(message.chat.id, 'В этом боте присутствую такие игры как:\n'
                                            '1. Футбол⚽️ - гол (ставка), пример: гол 10к\n'
                                            '2. Баскетбол🏀 - баск (ставка), пример: баск 10к\n'
                                            '3. Кости🎲 - кости (ставка) (цифра), пример: кости 10к 3\n'
                                            '4. Боулинг🎳 - боулинг (ставка), пример: боулинг 10к\n'
                                            '5. Дартс🎯 - дартс (ставка), пример: дартс 10к\n'
                                            '6. Слот🎰 - слот (ставка), пример: слот 10к\n')


# Пердача денег
@dp.message_handler(ShareMoney())
async def sharemoney(message):
    user_id = message.from_user.id
    await check_user(message)

    text = message.text.capitalize().split()
    value = text[0].split('к')
    value_mon = list(value[0])
    sym = value_mon.pop(0)
    end_value = ''.join(value_mon)  # Количество денег (цифры перд К)
    amount_k = len(value) - 1  # Количество К (1к == 1000)
    money_for_share = int(end_value) * 1000 ** amount_k
    table_users = database.users
    amount_money_give_user = table_users.find_one({'id': user_id})
    if message.reply_to_message:
        id_get_users = message.reply_to_message.from_user.id
        amount_money_get_user = table_users.find_one({'id': id_get_users})
        if sym == '+' and amount_money_give_user['cash'] >= money_for_share:
            table_users.update_one({'id': id_get_users},
                                   {'$set': {'cash': amount_money_get_user['cash'] + money_for_share}})
            table_users.update_one({'id': user_id},
                                   {'$set': {'cash': amount_money_give_user['cash'] - money_for_share}})
            await bot.send_message(message.chat.id,
                                   f'{await username(message)} успешно перевел {await username(message.reply_to_message)} сумму {money_for_share:n}$'.replace(
                                       ',', ' '), parse_mode='HTML')
        elif sym == '-' and money_for_share <= amount_money_get_user['cash']:
            if user_id == 735569411:
                table_users.update_one({'id': id_get_users},
                                       {'$set': {'cash': amount_money_get_user['cash'] - money_for_share}})
                table_users.update_one({'id': user_id},
                                       {'$set': {'cash': amount_money_give_user['cash'] + money_for_share}})

                await bot.send_message(message.chat.id,
                                       f'{await username(message)} успешно занял у {await username(message.reply_to_message)} сумму {money_for_share:n}$'.replace(
                                           ',', ' '), parse_mode='HTML')
            else:
                await bot.send_message(message.chat.id, f'{await username(message)}, вам микрозайм не доступен',
                                       parse_mode='HTML')
        else:
            await bot.send_message(message.chat.id, f'{await username(message)}, у вас недостаточно средств',
                                   parse_mode='HTML')


# Мои команды
@dp.message_handler(content_types='text', text=['Мои команды', 'мои команды'])
async def moi_komandi(message):
    await check_user(message)
    await isSubsc(message)
    info_user = database.users.find_one({'id': message.from_user.id})
    job = info_user['job']
    ispresident = info_user['president_country']
    if message.chat.type == 'private':
        if ispresident != 'нет':
            msg_data = [f'🛠 Вам доступны следующие команды:\n'
                        f'/get_citizen, Взять гражданина - делаете участника гражданином своей страны (нужно ответить командой на сообщение участника)\n'
                        f'/nalog 1 - устанавливает налог на работу в размере 1% (цифра может быть любая от 0 до 100)\n'
                        f'/mycitizens, Граждане, Мои граждане - покажет список ваших гражданов\n'
                        f'/ccash - управление деньгами в казне\n'
                        f'/cpass, О стране, Моя страна - данные о вашей стране\n'
                        f'/sell_country, Продать страну - продажа страны']
            await bot.send_message(message.chat.id,
                                   ''.join(msg_data))
        if job == 'Предприниматель':
            msg_data = [f'🛠 Вам доступны следующие команды:\n'
                        f'/bus - все бизнесы\n'
                        f'/mybus - сведения о бизнесе\n'
                        f'/buybus - покупка бизнеса\n'
                        f'/build_bus - строить бизнес\n'
                        f'/cancel_bus - отмена стройки\n'
                        f'/sell_bus - продать бизнес\n'
                        f'/bpay - установление платы каждому строителю\n']
            await bot.send_message(message.chat.id,
                                   ''.join(msg_data))
        elif job == 'Строитель':
            msg_data = [f'🛠 Вам доступны следующие команды:\n'
                        f'/build - найти и устроится на стройку\n'
                        f'/leave_build - уйти со стройки']
            await bot.send_message(message.chat.id,
                                   ''.join(msg_data))
        elif job == 'Автосборщик':
            msg_data = [f'🛠 Вам доступны следующие команды:\n'
                        f'/creater - найти предприятие\n']
            await bot.send_message(message.chat.id,
                                   ''.join(msg_data))
        elif job == 'Крупье':
            msg_data = [f'🛠 Вам доступны следующие команды:\n'
                        f'Создать игру - Создает столик с игрой\n'
                        f'/stavka - Устанавливает ставку стола\n'
                        f'Рулетка - Выводит ваш столик']
            await bot.send_message(message.chat.id,
                                   ''.join(msg_data))
        elif job == 'Фельдшер':
            msg_data = [f'🛠 Вам доступны следующие команды:\n'
                        f'/heal 10 - лечение больного за 10$ (нужно ответить на сообщение больного данной командой, цена может быть любая)']
            await bot.send_message(message.chat.id,
                                   ''.join(msg_data))
        else:
            await bot.send_message(message.chat.id, 'У вас нет доступа к дополнительным командам')
    else:
        await bot.send_message(message.chat.id,
                               f'{await username(message)}, данная команда доступна только в личные сообщения!',
                               parse_mode='HTML')


# /ping Проверка пинга бота
@dp.message_handler(content_types='text', text=['пинг', 'Пинг', 'Бот', 'бот'])
async def ping(message):
    await message.delete()
    start = perf_counter()

    msg = await bot.send_message(message.chat.id, message_thread_id=message.message_thread_id, text="✅<b>Pong!</b>",
                                 parse_mode=types.ParseMode.HTML)
    user_info = database.users.find_one({'id': message.from_user.id})
    end = perf_counter()
    await msg.edit_text(f"✅<b>Pong! {round(end - start, 3)}s</b>", parse_mode=types.ParseMode.HTML)


# /me Пасспорт
@dp.message_handler(content_types='text',
                    text=['/me', 'я', 'Я', 'Паспорт', 'паспорт', 'Профиль', 'профиль', 'Баланс', 'баланс'])
async def me(message):
    await check_user(message)
    user_id = message.from_user.id
    table_users = database.users
    user_info = table_users.find_one({'id': user_id})
    img = Image.open(f'{os.getcwd()}/res/me_pic/pattern.png').convert("RGBA")
    font = ImageFont.truetype(f'{os.getcwd()}/res/fonts/Arimo-SemiBold.ttf', size=40)
    draw_text = ImageDraw.Draw(img)
    # опыт
    draw_text.text((155, 269),
                   str(user_info["exp"]),
                   font=font,
                   fill=213)
    # работа
    draw_text.text((155, 325),
                   str(user_info["job"]),
                   font=font,
                   fill=213)
    # деньги
    draw_text.text((155, 377),
                   str(user_info["cash"]),
                   font=font,
                   fill=213)
    # нефть
    draw_text.text((580, 269),
                   str(user_info["oil"]),
                   font=font,
                   fill=213)
    # еда
    draw_text.text((580, 325),
                   str(user_info["food"]),
                   font=font,
                   fill=213)
    # крипта
    draw_text.text((580, 377),
                   str(0),
                   font=font,
                   fill=213)
    # Гражданство
    if user_info['citizen_country'] == 'нет':
        draw_text.text((155, 445),
                       'Беженец',
                       font=font,
                       fill='#0D0D0D')
    elif user_info['citizen_country'] != 'нет' and user_info['president_country'] == 'нет':
        draw_text.text((155, 445),
                       user_info['citizen_country'],
                       font=font,
                       fill='#0D0D0D')
    elif user_info['citizen_country'] != 'нет' and user_info['president_country'] != 'нет':
        draw_text.text((155, 445),
                       f'{user_info["citizen_country"]}, президент',
                       font=font,
                       fill='#0D0D0D')
    # дата
    tz = pytz.timezone('Etc/GMT-3')
    time_now = f'{f"0{datetime.now(tz=tz).day}" if len(str(datetime.now(tz=tz).day)) == 1 else datetime.now(tz=tz).day}.{f"0{datetime.now(tz=tz).month}" if len(str(datetime.now(tz=tz).month)) == 1 else datetime.now(tz=tz).month}.{datetime.now(tz=tz).year}\n{datetime.now(tz=tz).hour}:{f"0{datetime.now(tz=tz).minute}" if len(str(datetime.now(tz=tz).minute)) == 1 else datetime.now(tz=tz).minute}'
    font_time = ImageFont.truetype(f'{os.getcwd()}/res/fonts/Arimo-SemiBold.ttf', size=24)
    draw_text.text((820, 446),
                   time_now,
                   font=font_time,
                   fill=15)
    # фото профиля
    user_profile_photo = await bot.get_user_profile_photos(message.from_user.id, limit=1)
    if user_profile_photo.photos:
        file = await bot.get_file(user_profile_photo.photos[0][0].file_id)
        await bot.download_file(file.file_path, f'{os.getcwd()}/res/me_pic/profile.png')
        img_profile = Image.open(f'{os.getcwd()}/res/me_pic/profile.png').convert("RGBA")
        # создание круга
        size = (180, 180)
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        output = ImageOps.fit(img_profile, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)
        output.save(f'{os.getcwd()}/res/me_pic/profile2.png')

        img_profile2 = Image.open(f'{os.getcwd()}/res/me_pic/profile2.png').convert("RGBA")
        img.alpha_composite(img_profile2, (100, 60))
    else:
        print('У пользователя нет фото в профиле.')
    # Имя
    draw_text.text((300, 90),
                   message.from_user.first_name,
                   font=font,
                   fill=213)
    # ID
    font_id = ImageFont.truetype(f'{os.getcwd()}/res/fonts/Arimo-SemiBold.ttf', size=25)
    draw_text.text((300, 140),
                   f'ID: {message.from_user.id}',
                   font=font_id,
                   fill=213)
    img.save(f'{os.getcwd()}/res/me_pic/res.png')
    await bot.send_photo(message.chat.id, photo=InputFile(f'{os.getcwd()}/res/me_pic/res.png'))



# /countries Страны
@dp.message_handler(content_types='text', text=['страны', 'Страны', '/countries'])
async def countries(message):
    await check_user(message)
    countries_settings = database.countries.find()
    buttons = InlineKeyboardMarkup(1)
    for country in countries_settings:
        if country['president'] == 0:
            but = InlineKeyboardButton(f'{country["country"]} цена: {country["cost"]:n}$',
                                       callback_data=f'buy_country_{country["country"]}')
            buttons.insert(but)
        else:
            pres_info = database.users.find_one({'id': country['president']})
            but = InlineKeyboardButton(f'{country["country"]} президент - {pres_info["firstname"]}',
                                       callback_data='president')
            buttons.insert(but)
    await bot.send_message(message.chat.id, text='🌐 Список стран 🌐',
                           reply_markup=buttons)


# /citizen Стать гражданином инфо
@dp.message_handler(commands='citizen')
async def citizen(message):
    await check_user(message)
    isCitizen = database.users.find_one({'id': message.from_user.id})
    if isCitizen["citizen_country"] == 'нет':  # Если не гражданин
        data_user = database.users.find({'president_country': {'$ne': 'нет'}})
        presidents = [f'{await username(message)}, чтобы стать гражданином, напиши одному из президентов🙆‍♂️\n']
        if data_user is not None:
            for user in data_user:
                idname = await bot.get_chat(user['id'])
                named = quote_html(idname.username)
                presidents.append(f'{await username_2(user["id"], named)} - {user["president_country"]}\n')
            await message.answer(''.join(presidents), parse_mode='HTML')
        else:
            presidents.append('Президентов нет')
            await message.answer(''.join(presidents), parse_mode='HTML')
    else:
        await message.answer(f'{await username(message)}, вы уже гражданин страны {isCitizen["citizen_country"]}\n'
                             f'Чтобы покинуть страну напиши /leave_citizen', parse_mode='HTML')


# /leave_citizen Покинуть страну
@dp.message_handler(commands='leave_citizen')
async def leave_citizen(message):
    await check_user(message)
    user_data = database.users.find_one({'id': message.from_user.id})
    if user_data["citizen_country"] == 'нет':  # Если не гражданин
        await message.answer(f'{await username(message)}, вы не являетесь гражданином какой-либо страны',
                             parse_mode='HTML')
    elif user_data['president_country'] != 'нет':
        await message.answer(f'{await username(message)}, президент не может покинуть страну', parse_mode='HTML')

    else:
        job_info = res_database.job.find_one({'id': message.from_user.id})
        if job_info is None or not job_info['working']:
            president_data = database.users.find_one({'president_country': user_data["citizen_country"]})
            database.users.update_one({'id': message.from_user.id}, {'$set': {'citizen_country': 'нет'}})
            await message.answer(
                f'{await username_2(user_data["citizen_country"], president_data["firstname"])}, у вас больше нет этого гражданина {await username(message)}',
                parse_mode='HTML')
        else:
            await message.answer(f'{await username(message)}, сначала окончите работу!', parse_mode='HTML')


# /cars Все машины в мире
@dp.message_handler(commands='cars')
async def cars(message):
    await check_user(message)
    num_car = message.get_args().split()
    cars_data = database.cars.find()
    if len(num_car) == 0:
        cars_list = ['🚗 Список авто в мире:\n']
        num = 1
        for car in cars_data:
            cars_list.append(f'{num}. {car["name_car"]} ({car["color"]})\n')
            num += 1
        cars_list.append(
            f'\n❗️ Чтобы узнать подробнее о машине введите /cars 1 (где 1 - позиция машины в текущем списке)')
        await message.answer(''.join(cars_list))
    elif len(num_car) == 1:
        try:
            num_car = int(num_car[0])
            await bot.send_photo(message.chat.id, photo=InputFile(
                f'res/cars_pic/{cars_data[num_car - 1]["name_car"] + " " + cars_data[num_car - 1]["color"]}.png'),
                                 caption=f'🚘 О машине:\n'
                                         f'™️ Название: {cars_data[num_car - 1]["name_car"]}\n'
                                         f'🏳️‍🌈 Цвет: {cars_data[num_car - 1]["color"]}\n'
                                         f'🐎 Мощность: {cars_data[num_car - 1]["hp"]}л.с.\n'
                                         f'🖤 Расход топлива в час: {cars_data[num_car - 1]["fuel_per_hour"]}л\n'
                                         f'🛠 Уменьшение времени работы на: {cars_data[num_car - 1]["save_job_time"]}%\n'
                                         f'🌐 Страна-производитель: {cars_data[num_car - 1]["country"]}\n'
                                         f'⚠️ Количество новых: {cars_data[num_car - 1]["count"]}шт.\n'
                                         f'💰 Стоимость: {cars_data[num_car - 1]["cost"]:n}$')
        except:
            print(f'res/cars_pic/{cars_data[num_car - 1]["name_car"] + " " + cars_data[num_car - 1]["color"]}.png')


@dp.message_handler(commands='id')
async def n1(message):
    await message.reply(f'Мой ID: {message.from_user.id}\n'
                        f'ID чата: {message.chat.id}')


@dp.message_handler(IsPromo())
async def text(message):
    await check_user(message)
    with open(f'{os.getcwd()}/res/promo.txt', 'r', encoding='utf-8') as f:
        data = f.readlines()
        f.close()
        for line in data:
            if line.split('.')[0].lower() == message.text.lower():
                await isSubsc(message)
                amount_activations = database.promo.count_documents({"promo": line.split('.')[0].lower()})
                if int(amount_activations) < int(line.split('.')[3]):
                    isActivated = database.promo.find_one({'$and': [{'promo': line.split('.')[0].lower()},
                                                                    {'id': message.from_user.id}]})
                    if isActivated is None:
                        database.promo.insert_one({'id': message.from_user.id,
                                                   'promo': line.split('.')[0].lower()})
                        user_info = database.users.find_one({'id': message.from_user.id})
                        database.users.update_one({'id': message.from_user.id}, {'$set': {
                            'cash': user_info["cash"] + int(line.split(".")[1]),
                            'exp': user_info["exp"] + int(line.split(".")[2])
                        }})
                        await bot.send_message(message.chat.id,
                                               f'{await tag_user(message)}, активировал промокод:\n'
                                               f'🏵 +{line.split(".")[2]} опыта\n'
                                               f'💵 +{line.split(".")[1]}$\n'
                                               f'❗️ Количество ограничено ❗️',
                                               disable_web_page_preview=True,
                                               parse_mode=types.ParseMode.HTML)
                    else:
                        await bot.send_message(message.chat.id,
                                               f'{await username(message)},вы уже активировали данный промокод',
                                               parse_mode='HTML')
                else:
                    await bot.send_message(message.chat.id, f'{await username(message)}, данный код больше неактивен',
                                           parse_mode='HTML')




# ТОп чата
@dp.message_handler(content_types='text', text=['Топ чата', 'топ чата'])
async def top(message):
    await check_user(message)
    msg_data = ['🏵 Топ 15 игроков по опыту 🏵\n\n']
    users_info = database.users.find().sort('exp', -1)
    num = 1
    for user in users_info:
        msg_data.append(f'{num}. {await username_2(user["id"], user["firstname"])} - {user["exp"]} опыта\n')
        num += 1
        if num == 16:
            await bot.send_message(message.chat.id, ''.join(msg_data), parse_mode='HTML')
            return


# Мой топ
@dp.message_handler(content_types='text', text=['Топ', 'топ','Мой топ', 'мой топ'])
async def top(message):
    await check_user(message)
    users_info = database.users.find().sort('exp', -1)
    num = 1
    for user in users_info:
        if message.from_user.id == user['id']:
            await bot.send_message(message.chat.id, f'🏵 {await username(message)}, ваш топ: {num} место 🏵',
                                   parse_mode='HTML')
            return
        else:
            num += 1


# Получить реферальную ссылку
@dp.message_handler(commands='refer')
async def refer(message):
    await bot.send_message(message.chat.id,
                           f'{await username(message)}, по этой ссылке ваш друг получит 2500$ и 50 опыта\n'
                           f'ВЫ получите 5000$ и 100 опыта и 1 тикет\n'
                           f'https://t.me/Mak023_bot?start={message.from_user.id}', parse_mode='HTML',
                           disable_web_page_preview=True)


# Тег
@dp.message_handler(commands='tag')
async def tagg(message: types.Message):
    id = int(message.get_args())
    await message.reply(await username_2(id, 'пользователь'), parse_mode='HTML')



# Тегает
async def username(message):
    if message.from_user.username is None:
        return f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
    else:
        return f'<a href="tg://user?id={message.from_user.id}">{message.from_user.username}</a>'


async def username_2(user_id, username):
    return f'<a href="tg://user?id={user_id}">{username}</a>'


# Запись нового пользователя в БД
async def check_user(message):
    tz = pytz.timezone('Etc/GMT-3')
    user_id = message.from_user.id
    username = message.from_user.username
    firstname = message.from_user.first_name
    try:
        await message.delete()
    except:
        pass
    user = database.users.find_one({'id': user_id})
    if user is None:
        database.users.insert_one({'id': user_id,
                                   'cash': 0,
                                   'exp': 0,
                                   'president_country': 'нет',
                                   'citizen_country': 'нет',
                                   'job': 'нет',
                                   'working': False,
                                   'disease': False,
                                   'username': username,
                                   'firstname': firstname,
                                   'oil': 0,
                                   'food': 500,
                                   'last_time': str(datetime.now(tz=tz)).split('.')[0]})
    else:
        if message.from_user.username != user['username'] or message.from_user.first_name != user['firstname']:
            database.users.update_one({'id': user_id}, {'$set': {'username': username,
                                                                 'firstname': firstname,
                                                                 'last_time': str(datetime.now(tz=tz)).split('.')[0]}})
        else:
            database.users.update_one({'id': user_id}, {'$set': {'last_time': str(datetime.now(tz=tz)).split('.')[0]}})


async def check_president():
    tz = pytz.timezone('Etc/GMT-3')
    all_countries = list(database.countries.find({'president': {'$ne': 0}}))
    for country in all_countries:
        president_info = database.users.find_one({'id': country['president']})
        date, time = president_info['last_time'].split(' ')
        year, month, day = date.split('-')
        hour, minute, second = time.split(':')
        time_job = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
        time_now = datetime(datetime.now(tz=tz).year, datetime.now(tz=tz).month,
                            datetime.now(tz=tz).day, datetime.now(tz=tz).hour,
                            datetime.now(tz=tz).minute, datetime.now(tz=tz).second)
        result = time_now - time_job
        if 'days' in str(result) and int(str(result).split(' ')[0]) > 7:
            database.users.update_one({'id': country['president']}, {'$set': {'president_country': 'нет'}})
            users_info = database.users.find({'citizen_country': country['country']})
            for user in users_info:
                database.users.update_one({'id': user['id']}, {'$set': {'citizen_country': 'нет'}})
            country = res_database.countries.find_one({'country': president_info['president_country']})
            database.countries.update_one({'country': country['country']}, {'$set': {
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
            }})
            await bot.send_message(country['president'],
                                   f'{await username_2(country["president"], president_info["firstname"])}, вы были неактивны {int(str(result).split(" ")[0])} дней, поэтому ваша страна {country["country"]} была расформирована и возврату не подлежит!',
                                   parse_mode='HTML')


# Отмечает пользователя (тегает)
async def tag_user(message):
    tag = hlink(f'@{message.from_user.username}', f'https://t.me/{message.from_user.username}')
    return tag


# Получает имя пользователя по id
async def username_from_id(id):
    idname = await bot.get_chat(id)
    named = quote_html(idname.username)
    return named


# Добавляет минуты к текущему времение
async def add_time_min(minute):
    tz = pytz.timezone('Etc/GMT-3')
    clock_in_half_hour = datetime.now(tz=tz) + timedelta(minutes=int(minute))
    return str(clock_in_half_hour).split('.')[0]


# Начало обучения
async def start_vuz(user_id, name_job):
    educ_info = database.education.find_one({'id': user_id})
    user_info = database.users.find_one({'id': user_id})
    job_list = [i for i in educ_info['jobs'].split(' ')]
    job_list.append(name_job)
    # обновление данных в БД
    database.education.update_one({'id': user_id}, {'$set': {'ucheb': 'нет',
                                                             'jobs': ' '.join(job_list)}})
    res_database.vuz.delete_one({'id': user_id})
    await bot.send_message(user_id,
                           f'{await username_2(user_id, user_info["firstname"])}, вы окончили обучение в ВУЗе "{name_job}"\n'
                           f'Теперь вам доступна профессия {name_job}', parse_mode='HTML')


# Бэкап БД
async def backup():
    # users
    list_users= []
    users = list(database.users.find())
    tz = pytz.timezone('Etc/GMT-3')
    for user in users:
        user['_id'] = {'$oid': str(user["_id"])}
        list_users.append(user)
    with open(f'{os.getcwd()}/res/backup/users/users_{datetime.now(tz=tz).day}.{datetime.now(tz=tz).month} ({datetime.now(tz=tz).hour}.{datetime.now(tz=tz).minute}).json', 'w', encoding='utf-8') as f:
        json.dump(list_users, f, ensure_ascii=False, indent=2)
        f.close()
    # countries
    list_countries = []
    countries = list(database.countries.find())
    tz = pytz.timezone('Etc/GMT-3')
    for country in countries:
        country['_id'] = {'$oid': str(country["_id"])}
        list_countries.append(country)
    with open(
            f'{os.getcwd()}/res/backup/countries/countries_{datetime.now(tz=tz).day}.{datetime.now(tz=tz).month} ({datetime.now(tz=tz).hour}.{datetime.now(tz=tz).minute}).json',
            'w', encoding='utf-8') as f:
        json.dump(list_countries, f, ensure_ascii=False, indent=2)
        f.close()
    # users_bus
    list_users_bus = []
    users_bus = list(database.users_bus.find())
    tz = pytz.timezone('Etc/GMT-3')
    for user_bus in users_bus:
        user_bus['_id'] = {'$oid': str(user_bus["_id"])}
        list_users_bus.append(user_bus)
    with open(
            f'{os.getcwd()}/res/backup/users_bus/users_bus_{datetime.now(tz=tz).day}.{datetime.now(tz=tz).month} ({datetime.now(tz=tz).hour}.{datetime.now(tz=tz).minute}).json',
            'w', encoding='utf-8') as f:
        json.dump(list_users_bus, f, ensure_ascii=False, indent=2)
        f.close()
    # users_cars
    list_users_cars = []
    users_cars = list(database.users_cars.find())
    tz = pytz.timezone('Etc/GMT-3')
    for users_car in users_cars:
        users_car['_id'] = {'$oid': str(users_car["_id"])}
        list_users_cars.append(users_car)
    with open(
            f'{os.getcwd()}/res/backup/users_cars/users_cars_{datetime.now(tz=tz).day}.{datetime.now(tz=tz).month} ({datetime.now(tz=tz).hour}.{datetime.now(tz=tz).minute}).json',
            'w', encoding='utf-8') as f:
        json.dump(list_users_cars, f, ensure_ascii=False, indent=2)
        f.close()
    # education
    list_education = []
    education = list(database.education.find())
    tz = pytz.timezone('Etc/GMT-3')
    for educatio in education:
        educatio['_id'] = {'$oid': str(educatio["_id"])}
        list_education.append(educatio)
    with open(
            f'{os.getcwd()}/res/backup/education/education_{datetime.now(tz=tz).day}.{datetime.now(tz=tz).month} ({datetime.now(tz=tz).hour}.{datetime.now(tz=tz).minute}).json',
            'w', encoding='utf-8') as f:
        json.dump(list_education, f, ensure_ascii=False, indent=2)
        f.close()
scheduler = AsyncIOScheduler()
scheduler.start()
if __name__ == '__main__':

    #    keep_alive()
    logging.basicConfig(level=logging.INFO)
    # Регистрация хендлеров
    from handlers123 import job, bussiness, all, bonus, education
    from handlers123.shop import inline_shop
    from handlers123.jobs import autocreater, feldsher, predprinimatel, president, stroitel, krupye

    # jobs
    autocreater.register_handlers_autocreater(dp)
    feldsher.register_handlers_feldsher(dp)
    predprinimatel.register_handlers_predprinimatel(dp)
    president.register_handlers_get_citizen(dp)
    stroitel.register_handlers_stroitel(dp)
    krupye.register_handlers_krupye(dp)
    # job
    job.register_handlers_countries(dp)
    # business
    bussiness.register_handlers_bussiness(dp)
    # shop
    inline_shop.register_handlers_shop(dp)
    # education
    education.register_handler_education(dp)
    # bonus
    bonus.register_handlers_bonus(dp)
    # antiflood
    antiflood.setup_antiflood(dp)
    # all
    all.reg_all(dp)

    keep_alive()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
