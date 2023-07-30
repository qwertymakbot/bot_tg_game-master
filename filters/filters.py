from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
import os


class IsQuestions(BoundFilter):
    async def check(self, message: types.Message):
        text = message.text.capitalize().split()
        if 'бот' in text or 'Бот' in text:
            return True
        else:
            return False


class IsPromo(BoundFilter):
    async def check(self, message: types.Message):
        with open(f'{os.getcwd()}/res/promo.txt', 'r', encoding='utf-8') as f:
            data = f.readlines()
            f.close()
            for line in data:
                if line.split('.')[0].lower() == message.text.lower():
                    return True


# Фильтр футбол
class IsFootbal(BoundFilter):
    async def check(self, message: types.Message):
        text = message.text.capitalize().split()
        try:
            value = text[1].split('к')
            money_num = value.pop(0)  # Количество денег (цифры перд К)
            amount_k = len(value)  # Количество К (1к == 1000)
            return text[0] == 'Гол' and len(text) == 2 and int(money_num) >= 1 and amount_k >= 0
        except IndexError:
            return False
        except ValueError:
            return False


# Фильтр баксетбол
class IsBasketball(BoundFilter):
    async def check(self, message: types.Message):
        text = message.text.capitalize().split()
        try:
            value = text[1].split('к')
            money_num = value.pop(0)  # Количество денег (цифры перд К)
            amount_k = len(value)  # Количество К (1к == 1000)
            return (text[0] == 'Баскетбол' or text[0] == 'Баск') and len(text) == 2 and int(
                money_num) >= 1 and amount_k >= 0
        except IndexError:
            return False
        except ValueError:
            return False


# Фильтр кости
class IsDice(BoundFilter):
    async def check(self, message: types.Message):
        text = message.text.capitalize().split()
        try:
            value = text[1].split('к')
            amount_point = text[2]
            money_num = value.pop(0)  # Количество денег (цифры перд К)
            amount_k = len(value)  # Количество К (1к == 1000)
            return text[0] == 'Кости' and len(text) == 3 and int(
                money_num) >= 1 and amount_k >= 0 and (1 <= int(amount_point) <= 6)
        except IndexError:
            return False
        except ValueError:
            return False


# Фильтр дартс
class IsDarts(BoundFilter):
    async def check(self, message: types.Message):
        text = message.text.capitalize().split()
        try:
            value = text[1].split('к')
            money_num = value.pop(0)  # Количество денег (цифры перд К)
            amount_k = len(value)  # Количество К (1к == 1000)
            return text[0] == 'Дартс' and len(text) == 2 and int(
                money_num) >= 1 and amount_k >= 0
        except IndexError:
            return False
        except ValueError:
            return False


# Фильтр боулинг
class IsBowling(BoundFilter):
    async def check(self, message: types.Message):
        text = message.text.capitalize().split()
        try:
            value = text[1].split('к')
            money_num = value.pop(0)  # Количество денег (цифры перд К)
            amount_k = len(value)  # Количество К (1к == 1000)
            return text[0] == 'Боулинг' and len(text) == 2 and int(
                money_num) >= 1 and amount_k >= 0
        except IndexError:
            return False
        except ValueError:
            return False


# Фильтр слот
class IsSlot(BoundFilter):
    async def check(self, message: types.Message):
        text = message.text.capitalize().split()
        try:
            value = text[1].split('к')
            money_num = value.pop(0)  # Количество денег (цифры перд К)
            amount_k = len(value)  # Количество К (1к == 1000)
            return text[0] == 'Слот' and len(text) == 2 and int(
                money_num) >= 1 and amount_k >= 0
        except IndexError:
            return False
        except ValueError:
            return False

# Передача денег
class ShareMoney(BoundFilter):
    async def check(self, message: types.Message):
        text = message.text.split()
        count_symbol = []
        for i in list(text[0]):
            if i == '-' or i == '+':
                count_symbol.append(i)
        if len(count_symbol) > 1:
            return False
        else:
            if len(text) == 1:
                list_text = list(text[0])
                if (list_text[0] == '-' or list_text[0] == '+' and list_text[-1] == 'к') or list_text[0] == '-' or \
                        list_text[0] == '+':
                    list_text.pop(0)
                    try:
                        if list_text[-1] == 'к':
                            while True:
                                try:
                                    list_text.remove('к')
                                except ValueError:
                                    break
                            money = ''.join(list_text)
                            try:
                                int(money)
                                return True
                            except ValueError:
                                return False
                        else:
                            money = ''.join(list_text)
                            try:
                                int(money)
                                return True
                            except ValueError:
                                return False
                    except IndexError:
                        pass