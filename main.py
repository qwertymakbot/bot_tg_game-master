from aiogram import executor, types, Dispatcher
import json
import logging
import sqlite3
import os
import time
from aiogram.utils.markdown import hlink
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from create_bot import dp
from create_bot import bot
from aiogram.utils.markdown import quote_html
from time import perf_counter
from aiogram.types import InputFile
import pytz
import datetime
import asyncio
from dateutil import parser
import random
import math
from gpytranslate import Translator
import openai
import openai_async
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import hmac
import json
import hashlib
import requests
from filters.filters import IsQuestions, IsPromo, IsFootbal, IsBasketball, IsDice, IsDarts, IsBowling, \
    IsSlot, ShareMoney
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont, ImageOps
from background import*
t = Translator()
openai.api_key = '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'

from pymongo.mongo_client import MongoClient

# БД
database = MongoClient(
    "mongodb+srv://maksemqwerty:maksem228@cluster0.mylnsur.mongodb.net/?retryWrites=true&w=majority").data

res_database = MongoClient(
    "mongodb+srv://maksemqwerty:maksem228@cluster0.mylnsur.mongodb.net/?retryWrites=true&w=majority").res

food_mak = 40
food_povar = 90
food_pekar = 70
food_fermer = 200
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
import locale

locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
#  Логгирование
logging.basicConfig(level=logging.INFO)

# Вызывается при старте
async def on_startup(_):

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
                                   f'Теперь вам доступна профессия {str(educ_info["ucheb"]).replace("ВУЗ", "").strip()}', parse_mode='HTML')
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
                    await end_job_citizen(info_job['id'], -1001529344518)
                else:
                    await end_job_no_citizen(info_job['id'], -1001529344518)
            else:
                citizen = database.users.find_one({'id': info_job['id']})['citizen_country']
                # Если гражданин
                if citizen != 'нет':
                    scheduler.add_job(end_job_citizen, "date",
                                      run_date=info_job['time'],
                                      args=(info_job['id'],info_job['id']), id=str(info_job['id']), timezone=tz)
                else:
                    scheduler.add_job(end_job_no_citizen, "date",
                                      run_date=info_job['time'],
                                      args=(info_job['id'], info_job['id']), id=str(info_job['id']), timezone=tz)
        except:
            pass
    print('Бот онлайн')

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
    try:

        user_info = database.users.find_one({'id': user_id})
        job_info = database.jobs.find_one({'name_job': user_info['job']})
        country_info = database.countries.find_one({'country': user_info['citizen_country']})
        if user_info['job'] == 'Работник мака':
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
            await bot.send_message(chat_id,
                                   f'{await username_2(user_id, user_info["firstname"])}, вы окончили работу и получили за это:\n'
                                   f'🏵 +{job_info["exp_for_job"]} опыта\n'
                                   f'💵 +{job_info["cash"] - round(int(job_info["cash"]) * (country_info["nalog_job"] / 100))}$\n'
                                   f'🍔 +{round(food_mak * 0.1)}кг пищи\n'
                                   f'Государству:\n'
                                   f'🍔 +{food_mak}кг пищи\n'
                                   f'💵 +{round(int(job_info["cash"] * (country_info["nalog_job"] / 100)))}',
                                   parse_mode='HTML')
        elif user_info['job'] == 'Повар':
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
            await bot.send_message(chat_id,
                                   f'{await username_2(user_id, user_info["firstname"])}, вы окончили работу и получили за это:\n'
                                   f'🏵 +{job_info["exp_for_job"]} опыта\n'
                                   f'💵 +{job_info["cash"] - round(int(job_info["cash"]) * (country_info["nalog_job"] / 100))}$\n'
                                   f'🍔 +{round(food_povar * 0.1)}кг пищи\n'
                                   f'Государству:\n'
                                   f'🍔 +{food_povar}кг пищи\n'
                                   f'💵 +{round(int(job_info["cash"] * (country_info["nalog_job"] / 100)))}',
                                   parse_mode='HTML')
        elif user_info['job'] == 'Пекарь' or user_info['job'] == 'Кондитер':
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
            await bot.send_message(chat_id,
                                   f'{await username_2(user_id, user_info["firstname"])}, вы окончили работу и получили за это:\n'
                                   f'🏵 +{job_info["exp_for_job"]} опыта\n'
                                   f'💵 +{job_info["cash"] - round(int(job_info["cash"]) * (country_info["nalog_job"] / 100))}$\n'
                                   f'🍔 +{round(food_pekar * 0.1)}кг пищи\n'
                                   f'Государству:\n'
                                   f'🍔 +{food_pekar}кг пищи\n'
                                   f'💵 +{round(int(job_info["cash"] * (country_info["nalog_job"] / 100)))}',
                                   parse_mode='HTML')
        elif user_info['job'] == 'Фермер':
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
            await bot.send_message(chat_id,
                                   f'{await username_2(user_id, user_info["firstname"])}, вы окончили работу и получили за это:\n'
                                   f'🏵 +{job_info["exp_for_job"]} опыта\n'
                                   f'💵 +{job_info["cash"] - round(int(job_info["cash"]) * (country_info["nalog_job"] / 100))}$\n'
                                   f'🍔 +{round(food_fermer * 0.1)}кг пищи\n'
                                   f'Государству:\n'
                                   f'🍔 +{food_fermer}кг пищи\n'
                                   f'💵 +{round(int(job_info["cash"] * (country_info["nalog_job"] / 100)))}',
                                   parse_mode='HTML')
        elif user_info['job'] == 'Нефтяник':
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
            await bot.send_message(chat_id,
                                   f'{await username_2(user_id, user_info["firstname"])}, вы окончили работу и получили за это:\n'
                                   f'🏵 +{job_info["exp_for_job"]} опыта\n'
                                   f'💵 +{job_info["cash"] - round(int(job_info["cash"]) * (country_info["nalog_job"] / 100))}$\n'
                                   f'🖤 +{round(oil * 0.1)}л\n'
                                   f'Государству:\n'
                                   f'🖤 +{oil}л\n'
                                   f'💵 +{round(int(job_info["cash"] * (country_info["nalog_job"] / 100)))}',
                                   parse_mode='HTML')
        elif user_info['job'] == 'нет':
            res_database.job.delete_one({'id': user_id})

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
            await bot.send_message(chat_id,
                                   f'{await username_2(user_id, user_info["firstname"])}, вы окончили работу и получили за это:\n'
                                   f'🏵 +{job_info["exp_for_job"]} опыта\n'
                                   f'💵 +{job_info["cash"] - round(int(job_info["cash"]) * (country_info["nalog_job"] / 100))}$\n'
                                   f'Государству:\n'
                                   f'💵 +{round(int(job_info["cash"] * (country_info["nalog_job"] / 100)))}',
                                   parse_mode='HTML')
    except:
        pass

async def isSubsc(message):
    members = await bot.get_chat_member(chat_id=-1001879290440, user_id=message.from_user.id)
    if members['status'] != 'left':
        return
    else:
        await bot.send_message(message.chat.id,
                               f'{await username(message)}, чтобы получить доступ к команде, вы должны состоять в моем канале @makbotinfo', parse_mode='HTML')

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
            database.users.update_one({'id': int(message.get_args().split(' ')[0])}, {'$set': {'cash': user_info["cash"] + 5000,
                                                                              'exp': user_info["exp"] + 100}})
            await bot.send_message(int(message.get_args().split(' ')[0]), 'Вам были начислены за приведенного друга:\n'
                                                    '    - 5000$\n'
                                                    '    - 100 опыта')

# /help Помощь
@dp.message_handler(commands='help')
async def help(message):
    await message.delete()
    await bot.send_message(message.chat.id, f'Я, паспорт, профиль, баланс - Мой профиль\n'
                                            f'Страны - Список стран\n'
                                            f'/citizen - Стать гражданином\n'
                                            f'/leave_citizen - Покинуть страну\n'
                                            f'/cars - Инфо о машинах\n'
                                            f'/shop - Магазин\n'
                                            f'/bonus - Получить бонус\n'
                                            f'/bus - Бизнесы\n'
                                            f'/games - Список игр\n'
                                            f'Работа, работать - Работать на работе\n'
                                            f'Работы - Список работ\n'
                                            f'Уволиться - Уволиться с работы\n'
                                            f'Мои команды - Выводит список доп. команд\n'
                                            f'Топ - Выводит топ игроков по опыту\n'
                                            f'Топ чата - Выводит топ чата\n'
                                            f'Пообщаться с ботом написать сообщение: Бот .... (пример: бот какая погода в бресте)\n'
                                            f'Мой канал: @makbotinfo')


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
    member = await bot.get_chat_member(message.chat.id, user_id)
    admin = member.is_chat_creator()
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
            if admin:
                table_users.update_one({'id': id_get_users},
                                       {'$set': {'cash': amount_money_get_user['cash'] - money_for_share}})
                table_users.update_one({'id': user_id},
                                       {'$set': {'cash': amount_money_give_user['cash'] + money_for_share}})

                await bot.send_message(message.chat.id,
                                       f'{await username(message)} успешно занял у {await username(message.reply_to_message)} сумму {money_for_share:n}$'.replace(
                                           ',', ' '), parse_mode='HTML')
            else:
                await bot.send_message(message.chat.id, f'{await username(message)}, вам микрозайм не доступен', parse_mode='HTML')
        else:
            await bot.send_message(message.chat.id, f'{await username(message)}, у вас недостаточно средств', parse_mode='HTML')


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
                               f'{await username(message)}, данная команда доступна только в личные сообщения!', parse_mode='HTML')


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
    time_now = f'{datetime.now(tz=tz).day}.{f"0{datetime.now(tz=tz).month}" if len(str(datetime.now(tz=tz).month)) == 1 else datetime.now(tz=tz).month}.{datetime.now(tz=tz).year}\n{datetime.now(tz=tz).hour}:{f"0{datetime.now(tz=tz).minute}" if len(str(datetime.now(tz=tz).minute)) == 1 else datetime.now(tz=tz).minute}'
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

    """await bot.send_message(message.chat.id,
                           text=f'🪪 <b>Паспорт</b> {await username(message)}\n'
                                f'💵 Деньги: {user_info["cash"]}$\n'
                                f'🏵 Опыт: {user_info["exp"]}\n'
                                f'👨‍⚖️Президент: {user_info["president_country"]}\n'
                                f'👨 Гражданин: {user_info["citizen_country"]}\n'
                                f'🛠 Работа: {user_info["job"]}\n'
                                f'🖤 Нефти: {user_info["oil"]}л\n'
                                f'🍔 Еды: {user_info["food"]}кг',
                           disable_web_page_preview=True,
                           parse_mode='HTML')"""


# /countries Страны
@dp.message_handler(content_types='text', text=['страны', 'Страны', '/countries'])
async def countries(message):
    await check_user(message)
    countries_settings = database.countries.find()
    # countries_settings = cur.execute("""SELECT country, cost, president FROM countries""").fetchall()
    buttons = InlineKeyboardMarkup(1)
    for country in countries_settings:
        if country['president'] == 0:
            but = InlineKeyboardButton(f'{country["country"]} цена: {country["cost"]:n}$',
                                       callback_data=f'buy_country_{country["country"]}')
            buttons.insert(but)
        else:
            idname = await bot.get_chat(country['president'])
            named = quote_html(idname.username)
            but = InlineKeyboardButton(f'{country["country"]} президент - {named}',
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
        await message.answer(f'{await username(message)}, вы не являетесь гражданином какой-либо страны', parse_mode='HTML')
    elif user_data['president_country'] != 'нет':
        await message.answer(f'{await username(message)}, президент не может покинуть страну', parse_mode='HTML')

    else:
        if not user_data['working']:
            president_data = database.users.find_one({'president_country': user_data["citizen_country"]})
            database.users.update_one({'id': message.from_user.id}, {'$set': {'citizen_country': 'нет'}})
            await message.answer(
                f'{await username_2(user_data["citizen_country"], president_data["firstname"])}, у вас больше нет этого гражданина {await username(message)}', parse_mode='HTML')
        else:
            try:
                await message.answer(f'{await username(message)}, сначала окончите работу!', parse_mode='HTML')
            except:
                database.users.update_one({'id': message.from_user.id}, {'$set': {'working': False}})
                database.users.update_one({'id': message.from_user.id}, {'$set': {'job': 'нет'}})
                await message.answer(f'{await username(message)}, вы покинули страну!', parse_mode='HTML')


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


@dp.message_handler(IsQuestions())
async def text(message):
    token_openai = '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'
    chats = [-1001769791322, -1001529344518]
    if message.reply_to_message and message.reply_to_message['from'][
        'is_bot'] and message.chat.id in chats or 'бот' in message.text.split() and message.chat.id in chats or 'Бот' in message.text.split() and message.chat.id in chats:

        msg = await bot.send_message(message.chat.id, f'{message.from_user.first_name}, ваш ответ обрабатывается!',
                                     reply_to_message_id=message.message_id)

        response = await openai_async.complete(
            token_openai,
            timeout=30,
            payload={
                "model": "text-davinci-003",
                "prompt": f"{message.text.capitalize().replace('бот', '')}",
                "max_tokens": 500,
                "temperature": 0,
                "top_p": 1,
                "n": 1

            },
        )
        await bot.edit_message_text(response.json()["choices"][0]["text"].strip(), message.chat.id, msg.message_id)
    elif message.reply_to_message and message.reply_to_message['from'][
        'is_bot'] and message.chat.id not in chats or 'бот' in message.text.split() and message.chat.id not in chats or 'Бот' in message.text.split() and message.chat.id not in chats:
        await message.answer(
            'Чтобы получить доступ к ИИ и получать ответы на все вопросы, обратитесь к моему разработчику @KJIUKU')


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
                        await bot.send_message(message.chat.id,f'{await username(message)},вы уже активировали данный промокод', parse_mode='HTML')
                else:
                    await bot.send_message(message.chat.id,f'{await username(message)}, данный код больше неактивен', parse_mode='HTML')


# Выигрыш
async def win(message, rate_money, amount_money, koff, user_id):
    win_money = int(rate_money * koff)
    end_amount_money = win_money + int(amount_money)
    database.users.update_one({'id': user_id}, {'$set': {'cash': int(end_amount_money)}})
    await asyncio.sleep(4)
    await bot.send_message(message.chat.id, f'{await username(message)}, ваш выигрыш ===> +' + str(
        f'{win_money:n}$'.replace(',', ' ')), parse_mode='HTML')


# Проигрыш
async def lose(message, amount_money, rate_money, user_id):
    end_amount_money = int(amount_money) - rate_money
    database.users.update_one({'id': user_id}, {'$set': {'cash': int(end_amount_money)}})
    await asyncio.sleep(4)
    await bot.send_message(message.chat.id, f'{await username(message)}, проигрыш ===> -' + str(
        f'{rate_money:n}$'.replace(',', ' ')), parse_mode='HTML')


# Выигрыш слот
async def win_slot(message, rate_money, amount_money, koff, user_id):
    win_money = int(rate_money * koff)
    end_amount_money = win_money + int(amount_money)
    database.users.update_one({'id': user_id}, {'$set': {'cash': int(end_amount_money)}})
    await asyncio.sleep(2)
    await bot.send_message(message.chat.id, f'{await username(message)}, ваш выигрыш ===> +' + str(
        f'{win_money:n}$'.replace(',', ' ')), parse_mode='HTML')


# Проигрыш слот
async def lose_slot(message, amount_money, rate_money, user_id):
    end_amount_money = int(amount_money) - rate_money
    database.users.update_one({'id': user_id}, {'$set': {'cash': int(end_amount_money)}})
    await asyncio.sleep(2)
    await bot.send_message(message.chat.id, f'{await username(message)}, проигрыш ===> -' + str(
        f'{rate_money:n}$'.replace(',', ' ')), parse_mode='HTML')


# Футбол
@dp.message_handler(IsFootbal())
async def get_game_data(message):
    user_id = message.from_user.id
    await check_user(message)

    text = message.text.capitalize().split()
    value = text[1].split('к')
    money_num = value.pop(0)  # Количество денег (цифры перд К)
    amount_k = len(value)  # Количество К (1к == 1000)
    rate_money = int(money_num) * 1000 ** amount_k  # Ставка
    user_info = database.users.find_one({'id': user_id})
    amount_money = user_info['cash']
    if rate_money <= amount_money:
        amount_score = await bot.send_dice(message.chat.id, emoji='⚽')
        if amount_score.dice.value == 3:
            await win(message, rate_money, amount_money, 0.5, user_id)
        elif amount_score.dice.value == 4:
            await win(message, rate_money, amount_money, 0.75, user_id)
        elif amount_score.dice.value == 5:
            await win(message, rate_money, amount_money, 1, user_id)
        else:
            await lose(message, amount_money, rate_money, user_id)
    else:
        enough_money = rate_money - int(amount_money)
        await bot.send_message(message.chat.id, f'{await username(message)}, вам не хватает: ' + f'{enough_money:n}$\n' + 'Ваш баланс: ' + f'{amount_money:n}$', parse_mode='HTML')


# Баскетбол
@dp.message_handler(IsBasketball())
async def get_game_data(message):
    user_id = message.from_user.id
    await check_user(message)

    text = message.text.capitalize().split()
    value = text[1].split('к')
    money_num = value.pop(0)  # Количество денег (цифры перд К)
    amount_k = len(value)  # Количество К (1к == 1000)
    rate_money = int(money_num) * 1000 ** amount_k  # Ставка
    user_info = database.users.find_one({'id': user_id})
    amount_money = user_info['cash']
    if rate_money <= amount_money:
        amount_score = await bot.send_dice(message.chat.id, emoji='🏀')
        if amount_score.dice.value == 4:
            await win(message, rate_money, amount_money, 0.5, user_id)
        elif amount_score.dice.value == 5:
            await win(message, rate_money, amount_money, 1, user_id)
        else:
            await lose(message, amount_money, rate_money, user_id)
    else:
        enough_money = rate_money - int(amount_money)
        await bot.send_message(message.chat.id,
                               f'{await username(message)}, вам не хватает: ' + f'{enough_money:n}$\n'.replace(',',
                                                                                                               ' ') + 'Ваш баланс: ' + f'{amount_money:n}$'.replace(
                                   ',', ' '), parse_mode='HTML')


# Кости
@dp.message_handler(IsDice())
async def dice(message):
    user_id = message.from_user.id
    await check_user(message)

    text = message.text.capitalize().split()
    value = text[1].split('к')
    money_num = value.pop(0)  # Количество денег (цифры перд К)
    amount_k = len(value)  # Количество К (1к == 1000)
    rate_money = int(money_num) * 1000 ** amount_k  # Ставка
    amount_point = text[2]  # Количество точек
    user_info = database.users.find_one({'id': user_id})
    amount_money = user_info['cash']
    if rate_money <= int(amount_money):
        amount_score = await bot.send_dice(message.chat.id, emoji='🎲')
        if int(amount_point) == int(amount_score.dice.value):
            await win(message, rate_money, amount_money, 2, user_id)
        elif abs(int(amount_point) - amount_score.dice.value) == 1:
            await win(message, rate_money, amount_money, 0.5, user_id)
        else:
            await lose(message, amount_money, rate_money, user_id)
    else:
        enough_money = rate_money - int(amount_money)
        await bot.send_message(message.chat.id,
                               f'{await username(message)}, вам не хватает: ' + f'{enough_money:n}$\n'.replace(',',
                                                                                                               ' ') + 'Ваш баланс: ' + f'{amount_money:n}$'.replace(
                                   ',', ' '), parse_mode='HTML')


# Дартс
@dp.message_handler(IsDarts())
async def darts(message):
    user_id = message.from_user.id
    await check_user(message)

    text = message.text.capitalize().split()
    value = text[1].split('к')
    money_num = value.pop(0)  # Количество денег (цифры перд К)
    amount_k = len(value)  # Количество К (1к == 1000)
    rate_money = int(money_num) * 1000 ** amount_k  # Ставка
    user_info = database.users.find_one({'id': user_id})
    amount_money = user_info['cash']
    if rate_money <= amount_money:
        amount_score = await bot.send_dice(message.chat.id, emoji='🎯')
        if amount_score.dice.value == 6:
            await win(message, rate_money, amount_money, 2, user_id)
        elif amount_score.dice.value == 5:
            await win(message, rate_money, amount_money, 0.5, user_id)
        else:
            await lose(message, amount_money, rate_money, user_id)
    else:
        enough_money = rate_money - int(amount_money)
        await bot.send_message(message.chat.id,
                               f'{await username(message)}, вам не хватает: ' + f'{enough_money:n}$\n'.replace(',',
                                                                                                               ' ') + 'Ваш баланс: ' + f'{amount_money:n}$'.replace(
                                   ',', ' '), parse_mode='HTML')


# Боулинг
@dp.message_handler(IsBowling())
async def bowling(message):
    user_id = message.from_user.id
    await check_user(message)

    text = message.text.capitalize().split()
    value = text[1].split('к')
    money_num = value.pop(0)  # Количество денег (цифры перд К)
    amount_k = len(value)  # Количество К (1к == 1000)
    rate_money = int(money_num) * 1000 ** amount_k  # Ставка
    user_info = database.users.find_one({'id': user_id})
    amount_money = user_info['cash']
    if rate_money <= amount_money:
        amount_score = await bot.send_dice(message.chat.id, emoji='🎳')
        if amount_score.dice.value == 6:
            await win(message, rate_money, amount_money, 2, user_id)
        elif amount_score.dice.value == 5:
            await win(message, rate_money, amount_money, 1, user_id)
        else:
            await lose(message, amount_money, rate_money, user_id)
    else:
        enough_money = rate_money - int(amount_money)
        await bot.send_message(message.chat.id,
                               f'{await username(message)}, вам не хватает: ' + f'{enough_money:n}$\n'.replace(',',
                                                                                                               ' ') + 'Ваш баланс: ' + f'{amount_money:n}$'.replace(
                                   ',', ' '), parse_mode='HTML')


# Слот
@dp.message_handler(IsSlot())
async def slot(message):
    user_id = message.from_user.id
    await check_user(message)

    text = message.text.capitalize().split()
    value = text[1].split('к')
    money_num = value.pop(0)  # Количество денег (цифры перд К)
    amount_k = len(value)  # Количество К (1к == 1000)
    rate_money = int(money_num) * 1000 ** amount_k  # Ставка
    user_info = database.users.find_one({'id': user_id})
    amount_money = user_info['cash']
    if rate_money <= amount_money:
        amount_score = await bot.send_dice(message.chat.id, emoji='🎰')

        if amount_score.dice.value == 64:
            await win_slot(message, rate_money, amount_money, 12, user_id)
        elif amount_score.dice.value in (1, 22, 43):
            await win_slot(message, rate_money, amount_money, 5, user_id)
        elif amount_score.dice.value in (16, 32, 48):
            await win_slot(message, rate_money, amount_money, 3, user_id)
        else:
            await lose_slot(message, amount_money, rate_money, user_id)
    else:
        enough_money = rate_money - amount_money
        await bot.send_message(message.chat.id,
                               f'{await username(message)}, вам не хватает: ' + f'{enough_money:n}$\n'.replace(',',
                                                                                                               ' ') + 'Ваш баланс: ' + f'{amount_money:n}$'.replace(
                                   ',', ' '), parse_mode='HTML')


# ТОп чата
@dp.message_handler(content_types='text', text=['Топ чата', 'топ чата'])
async def top(message):
    await check_user(message)
    msg_data = ['🏵 Топ 15 игроков по опыту 🏵\n\n']
    users_info = database.users.find().sort('exp', -1)
    num = 1
    for user in users_info:
        msg_data.append(f'{num}. {await username_2(user["id"], user["username"])} - {user["exp"]} опыта\n')
        num += 1
        if num == 16:
            await bot.send_message(message.chat.id, ''.join(msg_data), parse_mode='HTML')
            return


# Мой топ
@dp.message_handler(content_types='text', text=['Топ', 'топ'])
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
    await bot.send_message(message.chat.id, f'{await username(message)}, по этой ссылке ваш друг получит 2500$ и 50 опыта\n'
                                            f'ВЫ получите 5000$ и 100 опыта\n'
                                            f'https://t.me/Mak023_bot?start={message.from_user.id}', parse_mode='HTML')


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
                                   'food': 0})
    else:
        if message.from_user.username != user['username'] or message.from_user.first_name != user['firstname']:
            database.users.update_one({'id': user_id}, {'$set': {'username': username,
                                                                 'firstname': firstname}})


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
    await bot.send_message(user_id, f'{await username_2(user_id, user_info["firstname"])}, вы окончили обучение в ВУЗе "{name_job}"\n'
                                    f'Теперь вам доступна профессия {name_job}', parse_mode='HTML')

scheduler = AsyncIOScheduler()
scheduler.start()
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    # Регистрация хендлеров
    from handlers123 import job, bussiness, inline_cancel_bus, all, bonus, education
    from handlers123.shop import inline_shop
    from handlers123.jobs import autocreater, feldsher, predprinimatel, president, stroitel, krupye
    from handlers123 import joke

    # inline_get_job.register_handlers_jobs(dp)
    # inline_get_countries.register_handlers_countries(dp)
    inline_cancel_bus.register_handlers_cancel_bus(dp)
    # jobs
    autocreater.register_handlers_autocreater(dp)
    feldsher.register_handlers_feldsher(dp)
    predprinimatel.register_handlers_predprinimatel(dp)
    president.register_handlers_get_citizen(dp)
    stroitel.register_handlers_stroitel(dp)
    krupye.register_handlers_krupye(dp)
    # job
    job.register_handlers_countries(dp)
    # bussiness
    bussiness.register_handlers_bussiness(dp)
    # shop
    inline_shop.register_handlers_shop(dp)
    # education
    education.register_handler_education(dp)
    # joke
    joke.register_handlers_countries(dp)
    # bonus
    bonus.register_handlers_bonus(dp)

    # all
    all.reg_all(dp)

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
