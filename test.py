import random

from pymongo.mongo_client import MongoClient

# БД
database = MongoClient(
    "mongodb+srv://maksemqwerty:maksem228@cluster0.mylnsur.mongodb.net/?retryWrites=true&w=majority").data

res_database = MongoClient(
    "mongodb+srv://maksemqwerty:maksem228@cluster0.mylnsur.mongodb.net/?retryWrites=true&w=majority").res

info = list(database.cars.find())

for car in info:
    database.cars.update_one({'name_car': car['name_car']}, {'$set': {'cost': car['cost'] * random.randint(2,5)}})
