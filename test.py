from pymongo.mongo_client import MongoClient

# БД
database = MongoClient(
    "mongodb+srv://maksemqwerty:maksem228@cluster0.mylnsur.mongodb.net/?retryWrites=true&w=majority").data

res_database = MongoClient(
    "mongodb+srv://maksemqwerty:maksem228@cluster0.mylnsur.mongodb.net/?retryWrites=true&w=majority").res

info = list(database.users.find())

for user in info:
    database.users.update_one({'id': user["id"]},{'$set':{'job': 'нет'}
                               })
