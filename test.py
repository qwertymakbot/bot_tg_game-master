import random

from pymongo.mongo_client import MongoClient
from datetime import datetime
import pytz
# БД
database = MongoClient(
    "mongodb+srv://maksemqwerty:maksem228@cluster0.mylnsur.mongodb.net/?retryWrites=true&w=majority").data

res_database = MongoClient(
    "mongodb+srv://maksemqwerty:maksem228@cluster0.mylnsur.mongodb.net/?retryWrites=true&w=majority").res

info = list(database.businesses.find())

num = 0
for user in info:
    num += 1
    database.businesses.update_one({'product': user['product']}, {'$set': {'oil': user['oil'] * random.randint(100,200)}})
    print(f'{num} из {len(info)}')
