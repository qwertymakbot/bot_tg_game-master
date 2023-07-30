import random
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from bot import database, res_database
from create_bot import bot, dp, token

# cases


class Database:
    def __init__(self):
        ...

    async def give_prize_in_little_case(self, message: types.Message, prize):
        user = database.users.find_one({'id' : int(message.from_user.id)})
        if 'money' in prize[1]:
            user_balance = int(user['cash'])
            database.users.update_one({'id': message.from_user.id}, {'$set': {'cash': user_balance - 4000}})
            database.users.update_one({'id': message.from_user.id}, {'$set': {'cash': user_balance + prize[0]}})

        elif 'exp' in prize[1]:
            user_exp = int(user['exp'])
            database.users.update_one({'id': message.from_user.id}, {'$set': {'exp': user_exp + prize[0]}})

    async def give_prize_in_middle_case(self, message, prize):
        ...

    async def give_prize_in_big_case(self, message, prize):
        ...


class Cases:

    def __init__(self):
        ...

    async def open_little_case(self):
        prizes = ['money', 'exp']
        prize = random.choice(prizes)

        match prize:
            case 'money':
                rand = random.randint(0, 4)
                if rand == 1 or rand == 2:
                    money = random.randint(1000, 10000)
                    return [money, 'money']
                else:
                    money = random.randint(100, 5000)
                    return [money, 'money']

            case 'exp':
                rand = random.randint(0, 6)
                if rand == 1 or rand == 2:
                    exp = random.randint(50, 1000)
                    return [exp, 'exp']
                else:
                    exp = random.randint(50, 200)
                    return [exp, 'exp']

    async def open_middle_case(self, username):
        prizes = ['car', 'money', 'exp', 'class_in_school']
        prize = random.choice(prizes)
        match prize:
            case 'money':
                rand = random.randint(0, 7)
                if rand == 1 or rand == 2:
                    money = random.randint(1000, 15000)
                    print(f"{username} выиграл {money}$")
                    return [money, 'money']
                else:
                    money = random.randint(1000, 5000)
                    print(f'{username}  выиграл {money}$')
                    return [money, 'money']

            case 'exp':
                rand = random.randint(0, 7)
                if rand == 1 or rand == 2:
                    exp = random.randint(100, 1500)
                    print(f"{username} выиграл {exp} опыта")
                    return [exp, 'exp']
                else:
                    exp = random.randint(100, 500)
                    print(f'{username}  выиграл {exp} опыта')
                    return [exp, 'exp']

            case 'car':
                rand = random.randint(0, 7)
                if rand == 1 or rand == 2:
                    cars = ['mercedes', 'lada', 'dodge', 'toyota']
                    car = random.choice(cars)
                    print(f"{username} выиграл {car}")
                    return [car, 'car']
                else:
                    cars = ['lada', 'toyota', 'xuina']
                    car = random.choice(cars)
                    print(f'{username}  выиграл {car}')
                    return [car, 'car']

            case 'class_in_school':
                rand = random.randint(0, 10)
                if rand == 1 or rand == 2:
                    class_in_school = random.randint(0, 11)
                    print(f"{username} выиграл переход на {class_in_school} класс школы ")
                else:
                    print(f'{username} выиграл переход в следующий класс')

    async def open_big_case(self, username):
        prizes = ['car', 'money', 'exp', 'class_in_school']
        prize = random.choice(prizes)
        match prize:
            case 'money':
                rand = random.randint(0, 4)
                if rand == 1 or rand == 2:
                    money = random.randint(1000, 15000)
                    print(f"{username} выиграл {money}$")
                    return [money, 'money']
                else:
                    money = random.randint(1000, 5000)
                    print(f'{username}  выиграл {money}$')
                    return [money, 'money']

            case 'exp':
                rand = random.randint(0, 4)
                if rand == 1 or rand == 2:
                    exp = random.randint(100, 1500)
                    print(f"{username} выиграл {exp} опыта")
                    return [exp, 'exp']
                else:
                    exp = random.randint(100, 500)
                    print(f'{username}  выиграл {exp} опыта')
                    return [exp, 'exp']

            case 'car':
                rand = random.randint(0, 6)
                if rand == 1 or rand == 2:
                    cars = ['mercedes', 'lada', 'dodge', 'toyota']
                    car = random.choice(cars)
                    print(f"{username} выиграл {car}")
                    return [car, 'car']
                else:
                    cars = ['lada', 'toyota', 'mercedes']
                    car = random.choice(cars)
                    print(f'{username}  выиграл {car}')
                    return [car, 'car']

            case 'class_in_school':
                rand = random.randint(0, 8)
                if rand == 1 or rand == 2:
                    class_in_school = random.randint(0, 11)
                    print(f"{username} выиграл переход на {class_in_school} класс школы ")
                    return [class_in_school, 'class']
                else:
                    print(f'{username} выиграл переход в следующий класс')
                    return ['+1', 'class']


if __name__ == '__main__':
    case = Cases()
    Casse = case.open_little_case('Васян')
    print(Casse)
    db = Database()
    db.give_prize_in_little_case(Casse, 735569411)
    #case.open_middle_case('Степка')
    #case.open_big_case('Масимка')
