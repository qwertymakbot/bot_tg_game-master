import random

from pymongo.mongo_client import MongoClient
from datetime import datetime
import pytz
# БД
database = MongoClient(
    "mongodb+srv://maksemqwerty:maksem228@cluster0.mylnsur.mongodb.net/?retryWrites=true&w=majority").data

res_database = MongoClient(
    "mongodb+srv://maksemqwerty:maksem228@cluster0.mylnsur.mongodb.net/?retryWrites=true&w=majority").res

info = list(database.users.find())

num = 0
for user in info:
    num += 1
    tz = pytz.timezone('Etc/GMT-3')
    database.users.update_one({'id': user['id']}, {'$set': {'last_time': str(datetime.now(tz=tz)).split('.')[0]}})
    print(f'{num} из {len(info)}')
