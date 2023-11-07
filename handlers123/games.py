from bot import InlineKeyboardButton, InlineKeyboardMarkup, database, res_database, username, check_user
from aiogram import types, Dispatcher, executor
from create_bot import dp, bot
import asyncio
from filters.filters import IsQuestions, IsPromo, IsFootbal, IsBasketball, IsDice, IsDarts, IsBowling, \
    IsSlot, ShareMoney
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
            await win(message, rate_money, amount_money, 0.25, user_id)
        elif amount_score.dice.value == 4:
            await win(message, rate_money, amount_money, 0.25, user_id)
        elif amount_score.dice.value == 5:
            await win(message, rate_money, amount_money, 0.45, user_id)
        else:
            await lose(message, amount_money, rate_money, user_id)
    else:
        enough_money = rate_money - int(amount_money)
        await bot.send_message(message.chat.id,
                               f'{await username(message)}, вам не хватает: ' + f'{enough_money:n}$\n' + 'Ваш баланс: ' + f'{amount_money:n}$',
                               parse_mode='HTML')


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
            await win(message, rate_money, amount_money, 1, user_id)
        elif amount_score.dice.value == 5:
            await win(message, rate_money, amount_money, 0.7, user_id)
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
            await win(message, rate_money, amount_money, 1, user_id)
        elif amount_score.dice.value == 5:
            await win(message, rate_money, amount_money, 0.7, user_id)
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
