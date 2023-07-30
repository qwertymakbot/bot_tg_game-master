import random

#cases
class Cases:

    def __init__(self):
        ...

    def open_little_case(self, username):
        prizes = ['money', 'exp']
        prize = random.choice(prizes)

        match prize:
            case 'money':
                rand = random.randint(0, 4)
                if rand == 1 or rand == 2:
                    money = random.randint(1000, 10000)
                    print(f"{username} выиграл {money}$")
                else:
                    money = random.randint(100, 5000)
                    print(f'{username}  выиграл {money}$')

            case 'exp':
                rand = random.randint(0, 6)
                if rand == 1 or rand == 2:
                    exp = random.randint(50, 1000)
                    print(f"{username} выиграл {exp} опыта")
                else:
                    exp = random.randint(50,200)
                    print(f'{username}  выиграл {exp} опыта')

    def open_middle_case(self, username):
        prizes = ['car', 'money', 'exp', 'class_in_school']
        prize = random.choice(prizes)
        match prize:
            case 'money':
                rand = random.randint(0, 7)
                if rand == 1 or rand == 2:
                    money = random.randint(1000, 15000)
                    print(f"{username} выиграл {money}$")
                else:
                    money = random.randint(1000, 5000)
                    print(f'{username}  выиграл {money}$')

            case 'exp':
                rand = random.randint(0, 7)
                if rand == 1 or rand == 2:
                    exp = random.randint(100, 1500)
                    print(f"{username} выиграл {exp} опыта")
                else:
                    exp = random.randint(100, 500)
                    print(f'{username}  выиграл {exp} опыта')

            case 'car':
                rand = random.randint(0, 7)
                if rand == 1 or rand == 2:
                    cars = ['mercedes', 'lada', 'dodge', 'toyota']
                    car = random.choice(cars)
                    print(f"{username} выиграл {car}")
                else:
                    cars = ['lada', 'toyota', 'xuina']
                    car = random.choice(cars)
                    print(f'{username}  выиграл {car}')

            case 'class_in_school':
                rand = random.randint(0, 10)
                if rand == 1 or rand == 2:
                    class_in_school = random.randint(0, 11)
                    print(f"{username} выиграл переход на {class_in_school} класс школы ")
                else:
                    print(f'{username} выиграл переход в следующий класс')


    def open_big_case(self, username):
        prizes = ['car', 'money', 'exp', 'class_in_school']
        prize = random.choice(prizes)
        match prize:
            case 'money':
                rand = random.randint(0, 4)
                if rand == 1 or rand == 2:
                    money = random.randint(1000, 15000)
                    print(f"{username} выиграл {money}$")
                else:
                    money = random.randint(1000, 5000)
                    print(f'{username}  выиграл {money}$')

            case 'exp':
                rand = random.randint(0, 4)
                if rand == 1 or rand == 2:
                    exp = random.randint(100, 1500)
                    print(f"{username} выиграл {exp} опыта")
                else:
                    exp = random.randint(100, 500)
                    print(f'{username}  выиграл {exp} опыта')

            case 'car':
                rand = random.randint(0, 6)
                if rand == 1 or rand == 2:
                    cars = ['mercedes', 'lada', 'dodge', 'toyota']
                    car = random.choice(cars)
                    print(f"{username} выиграл {car}")
                else:
                    cars = ['lada', 'toyota', 'mercedes']
                    car = random.choice(cars)
                    print(f'{username}  выиграл {car}')

            case 'class_in_school':
                rand = random.randint(0, 8)
                if rand == 1 or rand == 2:
                    class_in_school = random.randint(0, 11)
                    print(f"{username} выиграл переход на {class_in_school} класс школы ")
                else:
                    print(f'{username} выиграл переход в следующий класс')


if __name__ == '__main__':
    case = Cases()
    case.open_little_case('Васян')
    case.open_middle_case('Степка')
    case.open_big_case('Масимка')
