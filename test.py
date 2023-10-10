import random

from pymongo.mongo_client import MongoClient
from datetime import datetime
import pytz, os
# БД
database = MongoClient(
    "mongodb+srv://maksemqwerty:maksem228@cluster0.mylnsur.mongodb.net/?retryWrites=true&w=majority").data

res_database = MongoClient(
    "mongodb+srv://maksemqwerty:maksem228@cluster0.mylnsur.mongodb.net/?retryWrites=true&w=majority").res

with open(f'{os.getcwd()}/res/countries.txt', 'r', encoding='utf-8') as f:
    while True:
        line = f.readline()
        if not line:
            break
        else:
            countries_settings = line.replace('\n', '').split('.')
            res_database.countries.insert_one({
                    'country': countries_settings[0],
                    'president': 0,
                    'cash': int(countries_settings[1]),
                    'oil': int(countries_settings[2]),
                    'food': int(countries_settings[3]),
                    'territory': int(countries_settings[4]),
                    'level': 0,
                    'max_people': int(countries_settings[5]),
                    'terr_for_farmers': int(countries_settings[6]),
                    'cost': int(countries_settings[7]),
                    'nalog_job': 1
                })

