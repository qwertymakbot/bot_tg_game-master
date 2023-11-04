import asyncio
import json
import os
import random

from aiogram.dispatcher import FSMContext
from bot import Dispatcher, check_user, database, types, InlineKeyboardButton, InlineKeyboardMarkup, \
    InputFile, quote_html, username, username_2, pytz, scheduler, add_time_min, res_database, start_vuz
from cases import Database, Cases, little_case, middle_case, big_case
from create_bot import bot


# Отмена
async def otmena(callback: types.CallbackQuery):
    await callback.message.delete()


async def all(callback: types.CallbackQuery, state: FSMContext):
    await check_user(callback)
    user_id = callback.from_user.id
    data_callback = callback.data
    path = os.getcwd()
    """🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽РУЛЕТКА🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽"""
    # Выбор стола в рулетке
    if 'rulette_' in data_callback:
        await check_user(callback)
        arr = next(os.walk(f'{path}/game/casino/games'))[2]
        for i in arr:
            with open(f'{path}/game/casino/games/{i}', 'r', encoding='utf-8') as f:
                data = json.load(f)
                f.close()
                if str(callback.from_user.id) in data['игроки']:
                    await callback.answer(f'Вы уже играете за столиком!')
                    return
        with open(f'{path}/game/casino/games/{data_callback.replace("rulette_", "")}', 'r', encoding='utf-8') as f:
            data = json.load(f)
            f.close()
            if len(data['игроки']) < data['макс_игроков']:
                if callback.from_user.id not in data['игроки']:
                    with open(f'{path}/game/casino/games/{data_callback.replace("rulette_", "")}', 'w',
                              encoding='utf-8') as f:
                        gamers = data['игроки']
                        gamers.append(callback.from_user.id)
                        data['игроки'] = gamers
                        json.dump(data, f)
                        f.close()

                        path = os.getcwd()
                        arr = next(os.walk(f'{path}/game/casino/games'))[2]
                        key = InlineKeyboardMarkup()
                        num = 1
                        for i in arr:
                            if str(callback.message.chat.id) in i:
                                with open(f'{path}/game/casino/games/{i}', 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                    f.close()
                                    if len(data['игроки']) < data['макс_игроков']:
                                        but = InlineKeyboardButton(
                                            f'{num} столик ({len(data["игроки"])} из {data["макс_игроков"]} чел) Ставка: {data["ставка"]}$ ✅',
                                            callback_data=f'rulette_{i}')
                                        num += 1
                                        key.add(but)
                                    else:
                                        but = InlineKeyboardButton(
                                            f'{num} столик ({len(data["игроки"])} из {data["макс_игроков"]} чел) Ставка: {data["ставка"]}$ ❌',
                                            callback_data=f'rulette_{i}')
                                        num += 1
                                        key.add(but)
                        await bot.edit_message_text(f'Выберите столик:', chat_id=callback.message.chat.id,
                                                    message_id=callback.message.message_id, reply_markup=key)
                        await callback.answer(f'Вы успешно присоединились к игре!')
                else:
                    await callback.answer(f'Вы уже в игре!')
            await callback.answer(f'Столик полный!')
    # Ставка на цифры
    if 'ruletke_choice_' in data_callback:
        data = data_callback.replace('ruletke_choice_', '').split('_')
        user_info = database.users.find_one({'id': user_id})
        if user_info["job"] != 'Крупье':
            with open(f'{os.getcwd()}/game/casino/games/{data[2]}_{data[3]}.json', 'r', encoding='utf-8') as f:
                game_data = json.load(f)
                f.close()
                # Если пользователь находится за столиком
                if callback.from_user.id in game_data['игроки']:
                    stvka = game_data['ставка']
                    # Если баланс больше чем ставка
                    if user_info["cash"] >= stvka:
                        if game_data['запущ_рулетка']:
                            await callback.answer('Ожидайте пока рулетка прокрутится!')
                            return
                        # Отнимаем деньги из баланса
                        database.users.update_one({'id': user_id}, {'$set': {'cash': user_info['cash'] - stvka}})
                        users_stavki = game_data['ставки']
                        # если не делал ставок
                        list_users = []
                        for i in users_stavki:
                            list_users.append(list(i)[0])
                        # если ставок не было
                        if str(callback.from_user.id) not in list_users:
                            users_stavki.append({callback.from_user.id: {int(data[0]): int(stvka)}})
                            await callback.answer('Ставка сделана!')
                            await bot.answer_callback_query(callback.id, text="")
                            # Вывод сделаных ставок
                            arr = next(os.walk(f'{path}/game/casino/games'))[2]
                            num = 0
                            for i in arr:
                                if str(callback.message.chat.id) in i:
                                    num += 1
                                    if f'{data[2]}_{data[3]}.json' == i:
                                        key = InlineKeyboardMarkup(row_width=3)
                                        num_but1 = 1
                                        for a in range(0, 24):
                                            if num_but1 % 2 == 0:
                                                but1 = InlineKeyboardButton(f'{num_but1} 🔴',
                                                                            callback_data=f'ruletke_choice_{num_but1}_red_{callback.message.chat.id}_{data[3]}')
                                                key.insert(but1)
                                            else:
                                                but1 = InlineKeyboardButton(f'{num_but1} ⚫️',
                                                                            callback_data=f'ruletke_choice_{num_but1}_black_{callback.message.chat.id}_{data[3]}')
                                                key.insert(but1)
                                            num_but1 += 1
                                        but0 = InlineKeyboardButton(f'0 🟢',
                                                                    callback_data=f'ruletke_choice_0_green_{callback.message.chat.id}_{data[3]}')
                                        key.add(but0)
                                        # На красное
                                        red = InlineKeyboardButton(f'На красное 🔴',
                                                                   callback_data=f'ruletke_only_красное_{callback.message.chat.id}_{data[3]}')
                                        # На черное
                                        black = InlineKeyboardButton(f'На черное ⚫️',
                                                                     callback_data=f'ruletke_only_черное_{callback.message.chat.id}_{data[3]}')
                                        key.add(red, black)
                                        # все На красное
                                        all_red = InlineKeyboardButton(f'Все на красное 🔴',
                                                                       callback_data=f'ruletke_all_красное_{callback.message.chat.id}_{data[3]}')
                                        # все На черное
                                        all_black = InlineKeyboardButton(f'Все на черное ⚫️',
                                                                         callback_data=f'ruletke_all_черное_{callback.message.chat.id}_{data[3]}')
                                        # все На зеленое
                                        all_green = InlineKeyboardButton(f'Все на зеленое 🟢',
                                                                         callback_data=f'ruletke_all_зеленое_{callback.message.chat.id}_{data[3]}')
                                        key.add(all_red, all_black, all_green)

                                        spin = InlineKeyboardButton(f'Крутить рулетку',
                                                                    callback_data=f'ruletke_spin_{callback.message.chat.id}_{data[3]}')
                                        update = InlineKeyboardButton(f'Обновить ставки',
                                                                      callback_data=f'ruletke_update_{callback.message.chat.id}_{data[3]}')
                                        key.add(spin, update)

                                        leave = InlineKeyboardButton(f'Уйти из игры',
                                                                     callback_data=f'ruletke_leave_{callback.message.chat.id}_{data[3]}')
                                        key.add(leave)
                                        # список игроков
                                        gamers = []

                                        for gamer in game_data['игроки']:
                                            gamer_info = database.users.find_one({'id': gamer})
                                            gamers.append(f'@{gamer_info["username"]} ')
                                        msg_data = [f'@{callback.from_user.username}, начал игру за {num} столиком!\n'
                                                    f'Внимание игроки: {"".join(gamers)}\n'
                                                    f'Делайте ставки, ставка стола: {game_data["ставка"]}$\n']
                                        stavki = game_data['ставки']
                                        chetn = ['2', '4', '6', '8', '10', '12', '14', '16', '18', '20', '22', '24']
                                        ne_chetn = ['1', '3', '5', '7', '9', '11', '13', '15', '17', '19', '21',
                                                    '23']
                                        for user in range(0, len(stavki)):
                                            us_info = database.users.find_one({'id': list(stavki[user])[0]})
                                            for num in list(stavki[user][list(stavki[user])[0]]):
                                                if num in chetn:
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num}🔴\n')
                                                elif num in ne_chetn:
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num}⚫️\n')
                                                elif num == '0':
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num}🟢\n')
                                                elif num == 'красное':
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num} 🔴\n')
                                                elif num == 'черное':
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num} ⚫️\n')
                                                elif num == 'зеленое':
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num} 🟢\n')
                                        await bot.edit_message_text(''.join(msg_data),
                                                                    chat_id=callback.message.chat.id,
                                                                    message_id=callback.message.message_id,
                                                                    reply_markup=key)
                        # если были ставки сделаны
                        else:
                            # все ставки
                            all_stavki = users_stavki[list_users.index(str(callback.from_user.id))][
                                str(callback.from_user.id)].keys()
                            # если ставка на цифру уже есть
                            if str(data[0]) in all_stavki:
                                amount_stavka = users_stavki[list_users.index(str(callback.from_user.id))][
                                    str(callback.from_user.id)][str(data[0])]
                                users_stavki[list_users.index(str(callback.from_user.id))][
                                    str(callback.from_user.id)][str(data[0])] = int(amount_stavka) + int(stvka)
                            else:
                                users_stavki[list_users.index(str(callback.from_user.id))][
                                    str(callback.from_user.id)].update({str(data[0]): int(stvka)})
                            await callback.answer('Ставка сделана!')
                            await bot.answer_callback_query(callback.id, text="")
                            # Вывод сделаных ставок
                            arr = next(os.walk(f'{path}/game/casino/games'))[2]
                            num = 0
                            for i in arr:
                                if str(callback.message.chat.id) in i:
                                    num += 1
                                    if f'{data[2]}_{data[3]}.json' == i:
                                        key = InlineKeyboardMarkup(row_width=3)
                                        num_but1 = 1
                                        for a in range(0, 24):
                                            if num_but1 % 2 == 0:
                                                but1 = InlineKeyboardButton(f'{num_but1} 🔴',
                                                                            callback_data=f'ruletke_choice_{num_but1}_red_{callback.message.chat.id}_{data[3]}')
                                                key.insert(but1)
                                            else:
                                                but1 = InlineKeyboardButton(f'{num_but1} ⚫️',
                                                                            callback_data=f'ruletke_choice_{num_but1}_black_{callback.message.chat.id}_{data[3]}')
                                                key.insert(but1)
                                            num_but1 += 1
                                        but0 = InlineKeyboardButton(f'0 🟢',
                                                                    callback_data=f'ruletke_choice_0_green_{callback.message.chat.id}_{data[3]}')
                                        key.add(but0)
                                        # На красное
                                        red = InlineKeyboardButton(f'На красное 🔴',
                                                                   callback_data=f'ruletke_only_красное_{callback.message.chat.id}_{data[3]}')
                                        # На черное
                                        black = InlineKeyboardButton(f'На черное ⚫️',
                                                                     callback_data=f'ruletke_only_черное_{callback.message.chat.id}_{data[3]}')
                                        key.add(red, black)
                                        # все На красное
                                        all_red = InlineKeyboardButton(f'Все на красное 🔴',
                                                                       callback_data=f'ruletke_all_красное_{callback.message.chat.id}_{data[3]}')
                                        # все На черное
                                        all_black = InlineKeyboardButton(f'Все на черное ⚫️',
                                                                         callback_data=f'ruletke_all_черное_{callback.message.chat.id}_{data[3]}')
                                        # все На зеленое
                                        all_green = InlineKeyboardButton(f'Все на зеленое 🟢',
                                                                         callback_data=f'ruletke_all_зеленое_{callback.message.chat.id}_{data[3]}')
                                        key.add(all_red, all_black, all_green)

                                        spin = InlineKeyboardButton(f'Крутить рулетку',
                                                                    callback_data=f'ruletke_spin_{callback.message.chat.id}_{data[3]}')
                                        update = InlineKeyboardButton(f'Обновить ставки',
                                                                      callback_data=f'ruletke_update_{callback.message.chat.id}_{data[3]}')
                                        key.add(spin, update)

                                        leave = InlineKeyboardButton(f'Уйти из игры',
                                                                     callback_data=f'ruletke_leave_{callback.message.chat.id}_{data[3]}')
                                        key.add(leave)
                                        # список игроков
                                        gamers = []

                                        for gamer in game_data['игроки']:
                                            gamer_info = database.users.find_one({'id': gamer})
                                            gamers.append(f'@{gamer_info["username"]} ')
                                        msg_data = [f'@{callback.from_user.username}, начал игру за {num} столиком!\n'
                                                    f'Внимание игроки: {"".join(gamers)}\n'
                                                    f'Делайте ставки, ставка стола: {game_data["ставка"]}$\n']
                                        stavki = game_data['ставки']
                                        chetn = ['2', '4', '6', '8', '10', '12', '14', '16', '18', '20', '22', '24']
                                        ne_chetn = ['1', '3', '5', '7', '9', '11', '13', '15', '17', '19', '21',
                                                    '23']
                                        for user in range(0, len(stavki)):
                                            us_info = database.users.find_one({'id': list(stavki[user])[0]})
                                            for num in list(stavki[user][list(stavki[user])[0]]):
                                                if num in chetn:
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num}🔴\n')
                                                elif num in ne_chetn:
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num}⚫️\n')
                                                elif num == '0':
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num}🟢\n')
                                                elif num == 'красное':
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num} 🔴\n')
                                                elif num == 'черное':
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num} ⚫️\n')
                                                elif num == 'зеленое':
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num} 🟢\n')
                                        await bot.edit_message_text(''.join(msg_data),
                                                                    chat_id=callback.message.chat.id,
                                                                    message_id=callback.message.message_id,
                                                                    reply_markup=key)
                        game_data['ставки'] = users_stavki
                    # Недостаточно денег на балансе
                    else:
                        await callback.answer('Недостаточно средств!')
                # Не находится за столиком
                else:
                    await callback.answer('Вы не сидите за данным столиком!')
            with open(f'{path}/game/casino/games/{data[2]}_{data[3]}.json', 'w', encoding='utf-8') as f:
                json.dump(game_data, f)
                f.close()
            await callback.answer('Данная игра недействительна!')
        else:
            await callback.answer('Крупье не может играть!')
    # Ставки на цвета
    if 'ruletke_only_' in data_callback:
        color, chat_id, user_id = data_callback.replace('ruletke_only_', '').split('_')
        user_info = database.users.find_one({'id': user_id})
        if user_info["job"] != 'Крупье':
            with open(f'{os.getcwd()}/game/casino/games/{chat_id}_{user_id}.json', 'r', encoding='utf-8') as f:
                game_data = json.load(f)
                f.close()
                # Если пользователь находится за столиком
                if callback.from_user.id in game_data['игроки']:
                    stvka = game_data['ставка']
                    # Если баланс больше чем ставка
                    if user_info["cash"] >= stvka:
                        if game_data['запущ_рулетка']:
                            await callback.answer('Ожидайте пока рулетка прокрутится!')
                            return
                        # Отнимаем деньги из баланса
                        database.users.update_one({'id': user_id}, {'$set': {'cash': user_info['cash'] - stvka}})
                        users_stavki = game_data['ставки']
                        # если не делал ставок
                        list_users = []
                        for i in users_stavki:
                            list_users.append(list(i)[0])
                        # если ставок не было
                        if str(callback.from_user.id) not in list_users:
                            users_stavki.append({callback.from_user.id: {color: int(stvka)}})
                            await callback.answer('Ставка сделана!')
                            await bot.answer_callback_query(callback.id, text="")
                            # Вывод сделаных ставок
                            arr = next(os.walk(f'{path}/game/casino/games'))[2]
                            num = 0
                            for i in arr:
                                if str(callback.message.chat.id) in i:
                                    num += 1
                                    if f'{chat_id}_{user_id}.json' == i:
                                        key = InlineKeyboardMarkup(row_width=3)
                                        num_but1 = 1
                                        for a in range(0, 24):
                                            if num_but1 % 2 == 0:
                                                but1 = InlineKeyboardButton(f'{num_but1} 🔴',
                                                                            callback_data=f'ruletke_choice_{num_but1}_red_{callback.message.chat.id}_{user_id}')
                                                key.insert(but1)
                                            else:
                                                but1 = InlineKeyboardButton(f'{num_but1} ⚫️',
                                                                            callback_data=f'ruletke_choice_{num_but1}_black_{callback.message.chat.id}_{user_id}')
                                                key.insert(but1)
                                            num_but1 += 1
                                        but0 = InlineKeyboardButton(f'0 🟢',
                                                                    callback_data=f'ruletke_choice_0_green_{callback.message.chat.id}_{user_id}')
                                        key.add(but0)
                                        # На красное
                                        red = InlineKeyboardButton(f'На красное 🔴',
                                                                   callback_data=f'ruletke_only_красное_{callback.message.chat.id}_{user_id}')
                                        # На черное
                                        black = InlineKeyboardButton(f'На черное ⚫️',
                                                                     callback_data=f'ruletke_only_черное_{callback.message.chat.id}_{user_id}')
                                        key.add(red, black)
                                        # все На красное
                                        all_red = InlineKeyboardButton(f'Все на красное 🔴',
                                                                       callback_data=f'ruletke_all_красное_{callback.message.chat.id}_{user_id}')
                                        # все На черное
                                        all_black = InlineKeyboardButton(f'Все на черное ⚫️',
                                                                         callback_data=f'ruletke_all_черное_{callback.message.chat.id}_{user_id}')
                                        # все На зеленое
                                        all_green = InlineKeyboardButton(f'Все на зеленое 🟢',
                                                                         callback_data=f'ruletke_all_зеленое_{callback.message.chat.id}_{user_id}')
                                        key.add(all_red, all_black, all_green)

                                        spin = InlineKeyboardButton(f'Крутить рулетку',
                                                                    callback_data=f'ruletke_spin_{callback.message.chat.id}_{user_id}')
                                        update = InlineKeyboardButton(f'Обновить ставки',
                                                                      callback_data=f'ruletke_update_{callback.message.chat.id}_{user_id}')
                                        key.add(spin, update)

                                        leave = InlineKeyboardButton(f'Уйти из игры',
                                                                     callback_data=f'ruletke_leave_{callback.message.chat.id}_{user_id}')
                                        key.add(leave)
                                        # список игроков
                                        gamers = []

                                        for gamer in game_data['игроки']:
                                            gamer_info = database.users.find_one({'id': gamer})
                                            gamers.append(f'@{gamer_info["username"]} ')
                                        msg_data = [f'@{callback.from_user.username}, начал игру за {num} столиком!\n'
                                                    f'Внимание игроки: {"".join(gamers)}\n'
                                                    f'Делайте ставки, ставка стола: {game_data["ставка"]}$\n']
                                        stavki = game_data['ставки']
                                        chetn = ['2', '4', '6', '8', '10', '12', '14', '16', '18', '20', '22', '24']
                                        ne_chetn = ['1', '3', '5', '7', '9', '11', '13', '15', '17', '19', '21',
                                                    '23']
                                        for user in range(0, len(stavki)):
                                            us_info = database.users.find_one({'id': list(stavki[user])[0]})
                                            for num in list(stavki[user][list(stavki[user])[0]]):
                                                if num in chetn:
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num}🔴\n')
                                                elif num in ne_chetn:
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num}⚫️\n')
                                                elif num == '0':
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num}🟢\n')
                                                elif num == 'красное':
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num} 🔴\n')
                                                elif num == 'черное':
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num} ⚫️\n')
                                                elif num == 'зеленое':
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num} 🟢\n')
                                        await bot.edit_message_text(''.join(msg_data),
                                                                    chat_id=callback.message.chat.id,
                                                                    message_id=callback.message.message_id,
                                                                    reply_markup=key)
                        # если были ставки сделаны
                        else:
                            # все ставки
                            all_stavki = users_stavki[list_users.index(str(callback.from_user.id))][
                                str(callback.from_user.id)].keys()
                            # если ставка на цифру уже есть
                            if color in all_stavki:
                                amount_stavka = users_stavki[list_users.index(str(callback.from_user.id))][
                                    str(callback.from_user.id)][color]
                                users_stavki[list_users.index(str(callback.from_user.id))][
                                    str(callback.from_user.id)][color] = int(amount_stavka) + int(stvka)
                            else:
                                users_stavki[list_users.index(str(callback.from_user.id))][
                                    str(callback.from_user.id)].update({color: int(stvka)})
                            await callback.answer('Ставка сделана!')
                            await bot.answer_callback_query(callback.id, text="")
                            # Вывод сделаных ставок
                            arr = next(os.walk(f'{path}/game/casino/games'))[2]
                            num = 0
                            for i in arr:
                                if str(callback.message.chat.id) in i:
                                    num += 1
                                    if f'{chat_id}_{user_id}.json' == i:
                                        key = InlineKeyboardMarkup(row_width=3)
                                        num_but1 = 1
                                        for a in range(0, 24):
                                            if num_but1 % 2 == 0:
                                                but1 = InlineKeyboardButton(f'{num_but1} 🔴',
                                                                            callback_data=f'ruletke_choice_{num_but1}_red_{callback.message.chat.id}_{user_id}')
                                                key.insert(but1)
                                            else:
                                                but1 = InlineKeyboardButton(f'{num_but1} ⚫️',
                                                                            callback_data=f'ruletke_choice_{num_but1}_black_{callback.message.chat.id}_{user_id}')
                                                key.insert(but1)
                                            num_but1 += 1
                                        but0 = InlineKeyboardButton(f'0 🟢',
                                                                    callback_data=f'ruletke_choice_0_green_{callback.message.chat.id}_{user_id}')
                                        key.add(but0)
                                        # На красное
                                        red = InlineKeyboardButton(f'На красное 🔴',
                                                                   callback_data=f'ruletke_only_красное_{callback.message.chat.id}_{user_id}')
                                        # На черное
                                        black = InlineKeyboardButton(f'На черное ⚫️',
                                                                     callback_data=f'ruletke_only_черное_{callback.message.chat.id}_{user_id}')
                                        key.add(red, black)
                                        # все На красное
                                        all_red = InlineKeyboardButton(f'Все на красное 🔴',
                                                                       callback_data=f'ruletke_all_красное_{callback.message.chat.id}_{user_id}')
                                        # все На черное
                                        all_black = InlineKeyboardButton(f'Все на черное ⚫️',
                                                                         callback_data=f'ruletke_all_черное_{callback.message.chat.id}_{user_id}')
                                        # все На зеленое
                                        all_green = InlineKeyboardButton(f'Все на зеленое 🟢',
                                                                         callback_data=f'ruletke_all_зеленое_{callback.message.chat.id}_{user_id}')
                                        key.add(all_red, all_black, all_green)

                                        spin = InlineKeyboardButton(f'Крутить рулетку',
                                                                    callback_data=f'ruletke_spin_{callback.message.chat.id}_{user_id}')
                                        update = InlineKeyboardButton(f'Обновить ставки',
                                                                      callback_data=f'ruletke_update_{callback.message.chat.id}_{user_id}')
                                        key.add(spin, update)

                                        leave = InlineKeyboardButton(f'Уйти из игры',
                                                                     callback_data=f'ruletke_leave_{callback.message.chat.id}_{user_id}')
                                        key.add(leave)
                                        # список игроков
                                        gamers = []

                                        for gamer in game_data['игроки']:
                                            gamer_info = database.users.find_one({'id': gamer})
                                            gamers.append(f'@{gamer_info["username"]} ')
                                        msg_data = [f'@{callback.from_user.username}, начал игру за {num} столиком!\n'
                                                    f'Внимание игроки: {"".join(gamers)}\n'
                                                    f'Делайте ставки, ставка стола: {game_data["ставка"]}$\n']
                                        stavki = game_data['ставки']
                                        chetn = ['2', '4', '6', '8', '10', '12', '14', '16', '18', '20', '22', '24']
                                        ne_chetn = ['1', '3', '5', '7', '9', '11', '13', '15', '17', '19', '21',
                                                    '23']
                                        for user in range(0, len(stavki)):
                                            us_info = database.users.find_one({'id': list(stavki[user])[0]})
                                            for num in list(stavki[user][list(stavki[user])[0]]):
                                                if num in chetn:
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num}🔴\n')
                                                elif num in ne_chetn:
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num}⚫️\n')
                                                elif num == '0':
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num}🟢\n')
                                                elif num == 'красное':
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num} 🔴\n')
                                                elif num == 'черное':
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num} ⚫️\n')
                                                elif num == 'зеленое':
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num} 🟢\n')
                                        await bot.edit_message_text(''.join(msg_data),
                                                                    chat_id=callback.message.chat.id,
                                                                    message_id=callback.message.message_id,
                                                                    reply_markup=key)
                        game_data['ставки'] = users_stavki
                    # Недостаточно денег на балансе
                    else:
                        await callback.answer('Недостаточно средств!')
                # Не находится за столиком
                else:
                    await callback.answer('Вы не сидите за данным столиком!')
            with open(f'{path}/game/casino/games/{chat_id}_{user_id}.json', 'w', encoding='utf-8') as f:
                json.dump(game_data, f)
                f.close()
            await callback.answer('Данная игра недействительна!')
        else:
            await callback.answer('Крупье не может играть!')
    # Ставки на всё на цвета
    if 'ruletke_all_' in data_callback:
        color, chat_id, user_id = data_callback.replace('ruletke_all_', '').split('_')
        user_info = database.users.find_one({'id': user_id})
        if user_info["job"] != 'Крупье':
            with open(f'{os.getcwd()}/game/casino/games/{chat_id}_{user_id}.json', 'r', encoding='utf-8') as f:
                game_data = json.load(f)
                f.close()
                # Если пользователь находится за столиком
                if callback.from_user.id in game_data['игроки']:
                    stvka = user_info['cash']
                    # Если баланс больше чем ставка
                    if user_info['cash'] != 0:
                        if game_data['запущ_рулетка']:
                            await callback.answer('Ожидайте пока рулетка прокрутится!')
                            return
                        # Отнимаем деньги из баланса
                        database.users.update_one({'id': user_id}, {'$set': {'cash': 0}})
                        users_stavki = game_data['ставки']
                        # если не делал ставок
                        list_users = []
                        for i in users_stavki:
                            list_users.append(list(i)[0])
                        # если ставок не было
                        if str(callback.from_user.id) not in list_users:
                            users_stavki.append({callback.from_user.id: {color: int(stvka)}})
                            await callback.answer('Ставка сделана!')
                            await bot.answer_callback_query(callback.id, text="")
                            # Вывод сделаных ставок
                            arr = next(os.walk(f'{path}/game/casino/games'))[2]
                            num = 0
                            for i in arr:
                                if str(callback.message.chat.id) in i:
                                    num += 1
                                    if f'{callback.message.chat.id}_{callback.from_user.id}.json' == i:
                                        key = InlineKeyboardMarkup(row_width=3)
                                        num_but1 = 1
                                        for a in range(0, 24):
                                            if num_but1 % 2 == 0:
                                                but1 = InlineKeyboardButton(f'{num_but1} 🔴',
                                                                            callback_data=f'ruletke_choice_{num_but1}_red_{callback.message.chat.id}_{user_id}')
                                                key.insert(but1)
                                            else:
                                                but1 = InlineKeyboardButton(f'{num_but1} ⚫️',
                                                                            callback_data=f'ruletke_choice_{num_but1}_black_{callback.message.chat.id}_{user_id}')
                                                key.insert(but1)
                                            num_but1 += 1
                                        but0 = InlineKeyboardButton(f'0 🟢',
                                                                    callback_data=f'ruletke_choice_0_green_{callback.message.chat.id}_{user_id}')
                                        key.add(but0)
                                        # На красное
                                        red = InlineKeyboardButton(f'На красное 🔴',
                                                                   callback_data=f'ruletke_only_красное_{callback.message.chat.id}_{user_id}')
                                        # На черное
                                        black = InlineKeyboardButton(f'На черное ⚫️',
                                                                     callback_data=f'ruletke_only_черное_{callback.message.chat.id}_{user_id}')
                                        key.add(red, black)
                                        # все На красное
                                        all_red = InlineKeyboardButton(f'Все на красное 🔴',
                                                                       callback_data=f'ruletke_all_красное_{callback.message.chat.id}_{user_id}')
                                        # все На черное
                                        all_black = InlineKeyboardButton(f'Все на черное ⚫️',
                                                                         callback_data=f'ruletke_all_черное_{callback.message.chat.id}_{user_id}')
                                        # все На зеленое
                                        all_green = InlineKeyboardButton(f'Все на зеленое 🟢',
                                                                         callback_data=f'ruletke_all_зеленое_{callback.message.chat.id}_{user_id}')
                                        key.add(all_red, all_black, all_green)

                                        spin = InlineKeyboardButton(f'Крутить рулетку',
                                                                    callback_data=f'ruletke_spin_{callback.message.chat.id}_{user_id}')
                                        update = InlineKeyboardButton(f'Обновить ставки',
                                                                      callback_data=f'ruletke_update_{callback.message.chat.id}_{user_id}')
                                        key.add(spin, update)

                                        leave = InlineKeyboardButton(f'Уйти из игры',
                                                                     callback_data=f'ruletke_leave_{callback.message.chat.id}_{user_id}')
                                        key.add(leave)
                                        # список игроков
                                        gamers = []

                                        for gamer in game_data['игроки']:
                                            gamer_info = database.users.find_one({'id': gamer})
                                            gamers.append(f'@{gamer_info["username"]} ')
                                        msg_data = [f'@{callback.from_user.username}, начал игру за {num} столиком!\n'
                                                    f'Внимание игроки: {"".join(gamers)}\n'
                                                    f'Делайте ставки, ставка стола: {game_data["ставка"]}$\n']
                                        stavki = game_data['ставки']
                                        chetn = ['2', '4', '6', '8', '10', '12', '14', '16', '18', '20', '22', '24']
                                        ne_chetn = ['1', '3', '5', '7', '9', '11', '13', '15', '17', '19', '21',
                                                    '23']
                                        for user in range(0, len(stavki)):
                                            us_info = database.users.find_one({'id': list(stavki[user])[0]})
                                            for num in list(stavki[user][list(stavki[user])[0]]):
                                                if num in chetn:
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num}🔴\n')
                                                elif num in ne_chetn:
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num}⚫️\n')
                                                elif num == '0':
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num}🟢\n')
                                                elif num == 'красное':
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num} 🔴\n')
                                                elif num == 'черное':
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num} ⚫️\n')
                                                elif num == 'зеленое':
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num} 🟢\n')
                                        await bot.edit_message_text(''.join(msg_data),
                                                                    chat_id=callback.message.chat.id,
                                                                    message_id=callback.message.message_id,
                                                                    reply_markup=key)
                        # если были ставки сделаны
                        else:
                            # все ставки
                            all_stavki = users_stavki[list_users.index(str(callback.from_user.id))][
                                str(callback.from_user.id)].keys()
                            # если ставка на цифру уже есть
                            if color in all_stavki:
                                amount_stavka = users_stavki[list_users.index(str(callback.from_user.id))][
                                    str(callback.from_user.id)][color]
                                users_stavki[list_users.index(str(callback.from_user.id))][
                                    str(callback.from_user.id)][color] = int(amount_stavka) + int(stvka)
                            else:
                                users_stavki[list_users.index(str(callback.from_user.id))][
                                    str(callback.from_user.id)].update({color: int(stvka)})
                            await callback.answer('Ставка сделана!')
                            await bot.answer_callback_query(callback.id, text="")
                            # Вывод сделаных ставок
                            arr = next(os.walk(f'{path}/game/casino/games'))[2]
                            num = 0
                            for i in arr:
                                if str(callback.message.chat.id) in i:
                                    num += 1
                                    if f'{callback.message.chat.id}_{callback.from_user.id}.json' == i:
                                        key = InlineKeyboardMarkup(row_width=3)
                                        num_but1 = 1
                                        for a in range(0, 24):
                                            if num_but1 % 2 == 0:
                                                but1 = InlineKeyboardButton(f'{num_but1} 🔴',
                                                                            callback_data=f'ruletke_choice_{num_but1}_red_{callback.message.chat.id}_{user_id}')
                                                key.insert(but1)
                                            else:
                                                but1 = InlineKeyboardButton(f'{num_but1} ⚫️',
                                                                            callback_data=f'ruletke_choice_{num_but1}_black_{callback.message.chat.id}_{user_id}')
                                                key.insert(but1)
                                            num_but1 += 1
                                        but0 = InlineKeyboardButton(f'0 🟢',
                                                                    callback_data=f'ruletke_choice_0_green_{callback.message.chat.id}_{user_id}')
                                        key.add(but0)
                                        # На красное
                                        red = InlineKeyboardButton(f'На красное 🔴',
                                                                   callback_data=f'ruletke_only_красное_{callback.message.chat.id}_{user_id}')
                                        # На черное
                                        black = InlineKeyboardButton(f'На черное ⚫️',
                                                                     callback_data=f'ruletke_only_черное_{callback.message.chat.id}_{user_id}')
                                        key.add(red, black)
                                        # все На красное
                                        all_red = InlineKeyboardButton(f'Все на красное 🔴',
                                                                       callback_data=f'ruletke_all_красное_{callback.message.chat.id}_{user_id}')
                                        # все На черное
                                        all_black = InlineKeyboardButton(f'Все на черное ⚫️',
                                                                         callback_data=f'ruletke_all_черное_{callback.message.chat.id}_{user_id}')
                                        # все На зеленое
                                        all_green = InlineKeyboardButton(f'Все на зеленое 🟢',
                                                                         callback_data=f'ruletke_all_зеленое_{callback.message.chat.id}_{user_id}')
                                        key.add(all_red, all_black, all_green)

                                        spin = InlineKeyboardButton(f'Крутить рулетку',
                                                                    callback_data=f'ruletke_spin_{callback.message.chat.id}_{user_id}')
                                        update = InlineKeyboardButton(f'Обновить ставки',
                                                                      callback_data=f'ruletke_update_{callback.message.chat.id}_{user_id}')
                                        key.add(spin, update)

                                        leave = InlineKeyboardButton(f'Уйти из игры',
                                                                     callback_data=f'ruletke_leave_{callback.message.chat.id}_{user_id}')
                                        key.add(leave)
                                        # список игроков
                                        gamers = []

                                        for gamer in game_data['игроки']:
                                            gamer_info = database.users.find_one({'id': gamer})
                                            gamers.append(f'@{gamer_info["username"]} ')
                                        msg_data = [f'@{callback.from_user.username}, начал игру за {num} столиком!\n'
                                                    f'Внимание игроки: {"".join(gamers)}\n'
                                                    f'Делайте ставки, ставка стола: {game_data["ставка"]}$\n']
                                        stavki = game_data['ставки']
                                        chetn = ['2', '4', '6', '8', '10', '12', '14', '16', '18', '20', '22', '24']
                                        ne_chetn = ['1', '3', '5', '7', '9', '11', '13', '15', '17', '19', '21',
                                                    '23']
                                        for user in range(0, len(stavki)):
                                            us_info = database.users.find_one({'id': list(stavki[user])[0]})
                                            for num in list(stavki[user][list(stavki[user])[0]]):
                                                if num in chetn:
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num}🔴\n')
                                                elif num in ne_chetn:
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num}⚫️\n')
                                                elif num == '0':
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num}🟢\n')
                                                elif num == 'красное':
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num} 🔴\n')
                                                elif num == 'черное':
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num} ⚫️\n')
                                                elif num == 'зеленое':
                                                    msg_data.append(
                                                        f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num} 🟢\n')
                                        await bot.edit_message_text(''.join(msg_data),
                                                                    chat_id=callback.message.chat.id,
                                                                    message_id=callback.message.message_id,
                                                                    reply_markup=key)
                        game_data['ставки'] = users_stavki
                    # Недостаточно денег на балансе
                    else:
                        await callback.answer('Недостаточно средств!')
                # Не находится за столиком
                else:
                    await callback.answer('Вы не сидите за данным столиком!')
            with open(f'{path}/game/casino/games/{chat_id}_{user_id}.json', 'w', encoding='utf-8') as f:
                json.dump(game_data, f)
                f.close()
            await callback.answer('Данная игра недействительна!')
        else:
            await callback.answer('Крупье не может играть!')
    # Обновить ставки
    if 'ruletke_update_' in data_callback:
        user_info = database.users.find_one({'id': user_id})
        if user_info["job"] == 'Крупье':
            # Вывод сделаных ставок
            arr = next(os.walk(f'{os.getcwd()}/game/casino/games'))[2]
            num = 0
            for i in arr:
                if str(callback.message.chat.id) in i:
                    num += 1
                    if f'{callback.message.chat.id}_{callback.from_user.id}.json' == i:
                        key = InlineKeyboardMarkup(row_width=3)
                        num_but1 = 1
                        for a in range(0, 24):
                            if num_but1 % 2 == 0:
                                but1 = InlineKeyboardButton(f'{num_but1} 🔴',
                                                            callback_data=f'ruletke_choice_{num_but1}_red_{callback.message.chat.id}_{user_id}')
                                key.insert(but1)
                            else:
                                but1 = InlineKeyboardButton(f'{num_but1} ⚫️',
                                                            callback_data=f'ruletke_choice_{num_but1}_black_{callback.message.chat.id}_{user_id}')
                                key.insert(but1)
                            num_but1 += 1
                        but0 = InlineKeyboardButton(f'0 🟢',
                                                    callback_data=f'ruletke_choice_0_green_{callback.message.chat.id}_{user_id}')
                        key.add(but0)
                        # На красное
                        red = InlineKeyboardButton(f'На красное 🔴',
                                                   callback_data=f'ruletke_only_красное_{callback.message.chat.id}_{user_id}')
                        # На черное
                        black = InlineKeyboardButton(f'На черное ⚫️',
                                                     callback_data=f'ruletke_only_черное_{callback.message.chat.id}_{user_id}')
                        key.add(red, black)
                        # все На красное
                        all_red = InlineKeyboardButton(f'Все на красное 🔴',
                                                       callback_data=f'ruletke_all_красное_{callback.message.chat.id}_{user_id}')
                        # все На черное
                        all_black = InlineKeyboardButton(f'Все на черное ⚫️',
                                                         callback_data=f'ruletke_all_черное_{callback.message.chat.id}_{user_id}')
                        # все На зеленое
                        all_green = InlineKeyboardButton(f'Все на зеленое 🟢',
                                                         callback_data=f'ruletke_all_зеленое_{callback.message.chat.id}_{user_id}')
                        key.add(all_red, all_black, all_green)

                        spin = InlineKeyboardButton(f'Крутить рулетку',
                                                    callback_data=f'ruletke_spin_{callback.message.chat.id}_{user_id}')
                        update = InlineKeyboardButton(f'Обновить ставки',
                                                      callback_data=f'ruletke_update_{callback.message.chat.id}_{user_id}')
                        key.add(spin, update)

                        leave = InlineKeyboardButton(f'Уйти из игры',
                                                     callback_data=f'ruletke_leave_{callback.message.chat.id}_{user_id}')
                        key.add(leave)
                        with open(f'{path}/game/casino/games/{callback.message.chat.id}_{callback.from_user.id}.json',
                                  'r',
                                  encoding='utf-8') as f:
                            game_data = json.load(f)
                            f.close()
                            # список игроков
                            gamers = []

                            for gamer in game_data['игроки']:
                                gamer_info = database.users.find_one({'id': gamer})
                                gamers.append(f'@{gamer_info["username"]} ')
                            msg_data = [f'@{callback.from_user.username}, начал игру за {num} столиком!\n'
                                        f'Внимание игроки: {"".join(gamers)}\n'
                                        f'Делайте ставки, ставка стола: {game_data["ставка"]}$\n']
                            stavki = game_data['ставки']
                            chetn = ['2', '4', '6', '8', '10', '12', '14', '16', '18', '20', '22', '24']
                            ne_chetn = ['1', '3', '5', '7', '9', '11', '13', '15', '17', '19', '21',
                                        '23']
                            for user in range(0, len(stavki)):
                                us_info = database.users.find_one({'id': list(stavki[user])[0]})
                                for num in list(stavki[user][list(stavki[user])[0]]):
                                    if num in chetn:
                                        msg_data.append(
                                            f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num}🔴\n')
                                    elif num in ne_chetn:
                                        msg_data.append(
                                            f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num}⚫️\n')
                                    elif num == '0':
                                        msg_data.append(
                                            f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num}🟢\n')
                                    elif num == 'красное':
                                        msg_data.append(
                                            f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num} 🔴\n')
                                    elif num == 'черное':
                                        msg_data.append(
                                            f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num} ⚫️\n')
                                    elif num == 'зеленое':
                                        msg_data.append(
                                            f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num} 🟢\n')
                            try:
                                await bot.edit_message_text(''.join(msg_data),
                                                            chat_id=callback.message.chat.id,
                                                            message_id=callback.message.message_id,
                                                            reply_markup=key)
                                await callback.answer('Ставки обновлены!')
                            except:
                                await callback.answer('Ставки обновлены!')
    # Крутить рулетку
    if 'ruletke_spin_' in data_callback:
        # Множитель
        mn_num = 4  # если цифра
        mn_col = 2  # если цвет
        mn_green = 25  # если зеленый
        msg_data_stavki = []
        user_info = database.users.find_one({'id': user_id})
        arr = next(os.walk(f'{os.getcwd()}/game/casino/games'))[2]
        if f'{callback.message.chat.id}_{callback.from_user.id}.json' in arr:
            with open(f'{os.getcwd()}/game/casino/games/{callback.message.chat.id}_{callback.from_user.id}.json',
                      'r', encoding='utf-8') as f:
                data = json.load(f)
                f.close()
                stavki = data['ставки']
                for i in range(0, random.randint(3, 15)):
                    rnd_num = random.randint(0, 24)
                    # Вывод сделаных ставок
                    arr = next(os.walk(f'{path}/game/casino/games'))[2]
                    num = 0
                    for i in arr:
                        if str(callback.message.chat.id) in i:
                            num += 1
                            if f'{callback.message.chat.id}_{callback.from_user.id}.json' == i:
                                for gamer in game_data['игроки']:
                                    gamer_info = database.users.find_one({'id': gamer})
                                    gamers.append(f'@{gamer_info["username"]} ')
                                msg_data = [f'@{callback.from_user.username}, начал игру за {num} столиком!\n'
                                            f'Внимание игроки: {"".join(gamers)}\n'
                                            f'Делайте ставки, ставка стола: {game_data["ставка"]}$\n']
                                stavki = game_data['ставки']
                                chetn = ['2', '4', '6', '8', '10', '12', '14', '16', '18', '20', '22', '24']
                                ne_chetn = ['1', '3', '5', '7', '9', '11', '13', '15', '17', '19', '21',
                                            '23']
                                for user in range(0, len(stavki)):
                                    us_info = database.users.find_one({'id': list(stavki[user])[0]})
                                    for num in list(stavki[user][list(stavki[user])[0]]):
                                        if num in chetn:
                                            msg_data.append(
                                                f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num}🔴\n')
                                        elif num in ne_chetn:
                                            msg_data.append(
                                                f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num}⚫️\n')
                                        elif num == '0':
                                            msg_data.append(
                                                f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num}🟢\n')
                                        elif num == 'красное':
                                            msg_data.append(
                                                f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num} 🔴\n')
                                        elif num == 'черное':
                                            msg_data.append(
                                                f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num} ⚫️\n')
                                        elif num == 'зеленое':
                                            msg_data.append(
                                                f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num} 🟢\n')
                                    try:
                                        if rnd_num % 2 == 0:
                                            msg_data.append(f'\n\nВНИМАНИЕ РУЛЕТКА ЗАПУЩЕНА {rnd_num} 🔴')
                                        else:
                                            msg_data.append(f'\n\nВНИМАНИЕ РУЛЕТКА ЗАПУЩЕНА {rnd_num} ⚫️')
                                        await bot.edit_message_text(''.join(msg_data), callback.message.chat.id,
                                                                    callback.message.message_id)
                                        await asyncio.sleep(1)
                                    except:
                                        msg_data.pop(-1)
                                        rnd_num = random.randint(0, 24)
                                        if rnd_num % 2 == 0:
                                            msg_data.append(f'\n\nВНИМАНИЕ РУЛЕТКА ЗАПУЩЕНА {rnd_num} 🔴')
                                        else:
                                            msg_data.append(f'\n\nВНИМАНИЕ РУЛЕТКА ЗАПУЩЕНА {rnd_num} ⚫️')
                                        await bot.edit_message_text(''.join(msg_data), callback.message.chat.id,
                                                                    callback.message.message_id)
                                        await asyncio.sleep(0.7)
                rulettte_number = random.randint(0, 24)
                for user in stavki:
                    user_id = list(user.keys())[0]
                    stavki_user = user[user_id]
                    for stavka in list(stavki_user.keys()):
                        numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15',
                                   '16', '17', '18', '19', '20', '21', '22', '23', '24']
                        if stavka in numbers and stavka == str(rulettte_number):
                            database.users.update_one({'id': user_id}, {
                                '$set': {'cash': user_info["cash"] + (user[user_id][stavka] * mn_num)}})
                            if rulettte_number % 2 == 0:
                                msg_data_stavki.append(
                                    f'@{user_info["username"]} выиграл {user[user_id][stavka] * mn_num}$ на {stavka} 🔴\n')
                                del user[user_id][stavka]
                            else:
                                msg_data_stavki.append(
                                    f'@{user_info["username"]} выиграл {user[user_id][stavka] * mn_num}$ на {stavka} ⚫️\n')
                                del user[user_id][stavka]
                        elif stavka in numbers and stavka != str(rulettte_number):
                            if rulettte_number % 2 == 0:
                                msg_data_stavki.append(
                                    f'@{user_info["username"]} проиграл {user[user_id][stavka]}$ на {stavka} 🔴\n')
                                del user[user_id][stavka]
                            else:
                                msg_data_stavki.append(
                                    f'@{user_info["username"]} проиграл {user[user_id][stavka]}$ на {stavka} ⚫️\n')
                                del user[user_id][stavka]
                        elif stavka == str(rulettte_number) or stavka == 'зеленое' and str(rulettte_number) == '0':
                            database.users.update_one({'id': user_id}, {
                                '$set': {'cash': user_info["cash"] + (user[user_id][stavka] * mn_green)}})
                            msg_data_stavki.append(
                                f'@{user_info["username"]} выиграл {user[user_id][stavka] * mn_green}$ на {stavka} 🟢\n')
                            del user[user_id][stavka]
                        elif stavka == 'черное':
                            ne_chetn = ['1', '3', '5', '7', '9', '11', '13', '15', '17', '19', '21', '23']  # черное
                            if str(rulettte_number) in ne_chetn:
                                database.users.update_one({'id': user_id}, {
                                    '$set': {'cash': user_info["cash"] + (user[user_id][stavka] * mn_col)}})
                                msg_data_stavki.append(
                                    f'@{user_info["username"]} выиграл {user[user_id][stavka] * mn_col}$ на {stavka} ⚫️\n')
                                del user[user_id][stavka]
                            else:
                                msg_data_stavki.append(
                                    f'@{user_info["username"]} проиграл {user[user_id][stavka]}$ на {stavka} ⚫️\n')
                                del user[user_id][stavka]
                        elif stavka == 'красное':
                            chetn = ['2', '4', '6', '8', '10', '12', '14', '16', '18', '20', '22', '24']  # красное
                            if str(rulettte_number) in chetn:
                                database.users.update_one({'id': user_id}, {
                                    '$set': {'cash': user_info["cash"] + (user[user_id][stavka] * mn_col)}})
                                msg_data_stavki.append(
                                    f'@{user_info["username"]} выиграл {user[user_id][stavka] * mn_col}$ на {stavka} 🔴\n')
                                del user[user_id][stavka]
                            else:
                                msg_data_stavki.append(
                                    f'@{user_info["username"]} проиграл {user[user_id][stavka]}$ на {stavka} 🔴\n')
                                del user[user_id][stavka]
                if rulettte_number % 2 == 0:
                    msg_data_stavki.append(f'\n✨ Выпало число {rulettte_number}  🔴 ✨')
                else:
                    msg_data_stavki.append(f'\n✨ Выпало число {rulettte_number} ⚫️ ✨')
                game_data['ставки'] = []
                game_data['запущ_рулетка'] = False
                with open(
                        f'{os.getcwd()}/game/casino/games/{callback.message.chat.id}_{callback.from_user.id}.json',
                        'w', encoding='utf-8') as f:
                    json.dump(game_data, f)
                    f.close()
                await bot.edit_message_text(''.join(msg_data_stavki), callback.message.chat.id,
                                            callback.message.message_id)
        else:
            await callback.answer('Игра недействительна!')
    # Уйти со стола
    if 'ruletke_leave_' in data_callback:
        chat_id, user_id = data_callback.replace('ruletke_leave_', '').split('_')
        with open(f'{os.getcwd()}/game/casino/games/{chat_id}_{user_id}.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            f.close()
            num = 0
            for user in data['ставки']:
                if callback.from_user.id in list(user.keys()):
                    if list(user[callback.from_user.id].keys()) != 0:
                        await callback.answer(f'У вас есть ставки за данным столиком!')
                        return
                    else:
                        data['игроки'].remove(callback.from_user.id)
                        with open(f'{os.getcwd()}/game/casino/games/{chat_id}_{user_id}.json', 'w',
                                  encoding='utf-8') as f:
                            json.dump(data, f)
                            f.close()
                        await callback.answer('Вы вышли из игры!')
                        # Вывод сделаных ставок
                        arr = next(os.walk(f'{path}/game/casino/games'))[2]
                        num = 0
                        for i in arr:
                            if str(callback.message.chat.id) in i:
                                num += 1
                                if f'{chat_id}_{user_id}.json' == i:
                                    key = InlineKeyboardMarkup(row_width=3)
                                    num_but1 = 1
                                    for a in range(0, 24):
                                        if num_but1 % 2 == 0:
                                            but1 = InlineKeyboardButton(f'{num_but1} 🔴',
                                                                        callback_data=f'ruletke_choice_{num_but1}_red_{callback.message.chat.id}_{user_id}')
                                            key.insert(but1)
                                        else:
                                            but1 = InlineKeyboardButton(f'{num_but1} ⚫️',
                                                                        callback_data=f'ruletke_choice_{num_but1}_black_{callback.message.chat.id}_{user_id}')
                                            key.insert(but1)
                                        num_but1 += 1
                                    but0 = InlineKeyboardButton(f'0 🟢',
                                                                callback_data=f'ruletke_choice_0_green_{callback.message.chat.id}_{user_id}')
                                    key.add(but0)
                                    # На красное
                                    red = InlineKeyboardButton(f'На красное 🔴',
                                                               callback_data=f'ruletke_only_красное_{callback.message.chat.id}_{user_id}')
                                    # На черное
                                    black = InlineKeyboardButton(f'На черное ⚫️',
                                                                 callback_data=f'ruletke_only_черное_{callback.message.chat.id}_{user_id}')
                                    key.add(red, black)
                                    # все На красное
                                    all_red = InlineKeyboardButton(f'Все на красное 🔴',
                                                                   callback_data=f'ruletke_all_красное_{callback.message.chat.id}_{user_id}')
                                    # все На черное
                                    all_black = InlineKeyboardButton(f'Все на черное ⚫️',
                                                                     callback_data=f'ruletke_all_черное_{callback.message.chat.id}_{user_id}')
                                    # все На зеленое
                                    all_green = InlineKeyboardButton(f'Все на зеленое 🟢',
                                                                     callback_data=f'ruletke_all_зеленое_{callback.message.chat.id}_{user_id}')
                                    key.add(all_red, all_black, all_green)

                                    spin = InlineKeyboardButton(f'Крутить рулетку',
                                                                callback_data=f'ruletke_spin_{callback.message.chat.id}_{user_id}')
                                    update = InlineKeyboardButton(f'Обновить ставки',
                                                                  callback_data=f'ruletke_update_{callback.message.chat.id}_{user_id}')
                                    key.add(spin, update)

                                    leave = InlineKeyboardButton(f'Уйти из игры',
                                                                 callback_data=f'ruletke_leave_{callback.message.chat.id}_{user_id}')
                                    key.add(leave)
                                    # список игроков
                                    gamers = []

                                    for gamer in game_data['игроки']:
                                        gamer_info = database.users.find_one({'id': gamer})
                                        gamers.append(f'@{gamer_info["username"]} ')
                                    msg_data = [f'@{callback.from_user.username}, начал игру за {num} столиком!\n'
                                                f'Внимание игроки: {"".join(gamers)}\n'
                                                f'Делайте ставки, ставка стола: {game_data["ставка"]}$\n']
                                    stavki = game_data['ставки']
                                    chetn = ['2', '4', '6', '8', '10', '12', '14', '16', '18', '20', '22', '24']
                                    ne_chetn = ['1', '3', '5', '7', '9', '11', '13', '15', '17', '19', '21',
                                                '23']
                                    for user in range(0, len(stavki)):
                                        us_info = database.users.find_one({'id': list(stavki[user])[0]})
                                        for num in list(stavki[user][list(stavki[user])[0]]):
                                            if num in chetn:
                                                msg_data.append(
                                                    f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num}🔴\n')
                                            elif num in ne_chetn:
                                                msg_data.append(
                                                    f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num}⚫️\n')
                                            elif num == '0':
                                                msg_data.append(
                                                    f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num}🟢\n')
                                            elif num == 'красное':
                                                msg_data.append(
                                                    f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num} 🔴\n')
                                            elif num == 'черное':
                                                msg_data.append(
                                                    f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num} ⚫️\n')
                                            elif num == 'зеленое':
                                                msg_data.append(
                                                    f'{us_info["firstname"]} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num} 🟢\n')
                                    await bot.edit_message_text(''.join(msg_data),
                                                                chat_id=callback.message.chat.id,
                                                                message_id=callback.message.message_id,
                                                                reply_markup=key)
                else:
                    await callback.answer('Вы не сидите за данным столиком')
    """🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼РУЛЕТКА🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼"""

    """🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽ФЕЛЬДШЕР ДА НЕТ🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽"""
    if 'Фельдшер_да' in data_callback:
        data = data_callback.replace('Фельдшер_да.', '').split('.')
        if str(callback.from_user.id) == data[1]:
            heal_user = database.users.find_one({'id': int(data[0])})
            disease_user = database.users.find_one({'id': int(data[1])})

            database.users.update_one({'id': int(data[0])}, {'$set': {"cash": heal_user["cash"] + int(data[2])}})
            database.users.update_one({'id': int(data[1])}, {'$set': {"cash": disease_user["cash"] - int(data[2])}})

            res_database.disease.delete_one({'id': int(data[1])})

            await callback.answer(f'Вас успешно вылечили!')

            await bot.edit_message_text(
                f'{await username_2(int(data[0]), heal_user["username"])} успешно вылечил {await username_2(int(data[1]), disease_user["username"])} за {data[2]}$',
                callback.message.chat.id, callback.message.message_id, parse_mode='HTML')
            # Убирание задачи с болезнью
            scheduler.remove_job(str(callback.from_user.id))
        else:
            await callback.answer(f'Это предназначено не вам!')
    if 'Фельдшер_нет' in data_callback:
        data = data_callback.replace('Фельдшер_нет.', '').split('.')
        if str(callback.from_user.id) == data[1]:
            disease_user = database.users.find_one({'id': int(data[1])})
            await callback.answer(f'Вы отказались от лечения!')
            await bot.edit_message_text(
                f'{await username_2(int(data[1]), disease_user["username"])} отказался от лечения за {data[2]}$',
                callback.message.chat.id, callback.message.message_id, parse_mode='HTML')
        else:
            await callback.answer(f'Это предназначено не вам!')
    """🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼ФЕЛЬДШЕР ДА НЕТ🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼"""

    """🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽ПРОДАЖА СТРАНЫ🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽"""
    if 'sell_country_no_' in data_callback:
        data = data_callback.replace('sell_country_no_', '')
        if str(callback.from_user.id) == data:
            await callback.message.delete()
        else:
            await callback.answer(f'{await username(callback)}, это предназначено не вам!', parse_mode='HTML')
    if 'sell_country_' in data_callback:
        data = data_callback.replace('sell_country_', '').split('_')
        if str(callback.from_user.id) == data[0]:
            pres_info = database.users.find_one({'id': int(data[0])})
            database.users.update_one({'id': int(data[0])}, {'$set': {'president_country': 'нет'}})
            users_info = database.users.find({'citizen_country': data[1]})
            for user in users_info:
                database.users.update_one({'id': user['id']}, {'$set': {'citizen_country': 'нет'}})
            database.users.update_one({'id': int(data[0])}, {'$set': {'cash': pres_info['cash'] + int(data[2])}})
            country = res_database.countries.find_one({'country': pres_info['president_country']})
            database.countries.update_one({'country': country['country']},{'$set':{
                'president': 0,
                'cash': int(country['cash']),
                'oil': int(country['oil']),
                'food': int(country['food']),
                'territory': int(country['territory']),
                'level': 0,
                'max_people': int(country['max_people']),
                'terr_for_farmers': int(country['terr_for_farmers']),
                'cost': int(country['cost']),
                'nalog_job': 1
            }})
            await bot.edit_message_text(f'{await username(callback)} успешно продал {data[1]} за {data[2]}$',
                                        callback.message.chat.id, callback.message.message_id, parse_mode='HTML')
        else:
            await callback.answer(f'Это предназначено не вам!')
    """🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼ПРОДАЖА СТРАНЫ🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼"""

    """🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽ГРАЖДАНИН ДА НЕТ🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽"""
    if 'Гр_да_' in data_callback:
        data = data_callback.replace('Гр_да_', '').split('_')
        if str(callback.from_user.id) == data[1]:
            database.users.update_one({'id': int(data[1])}, {'$set': {'citizen_country': data[2]}})
            await callback.answer(f'Вы успешно стали гражданином!')
            pres_info = database.users.find_one({'id': int(data[0])})
            citiz_info = database.users.find_one({'id': int(data[1])})
            await callback.message.delete()
            await bot.send_photo(callback.message.chat.id,
                                 photo=InputFile(path + f'/res/country_pic/{data[2]}.png'),
                                 caption=f'{await username_2(int(data[0]), pres_info["username"])} у вас появился новый гражданин {await username_2(int(data[1]), citiz_info["username"])}',
                                 parse_mode='HTML')
        else:
            await callback.answer(f'Это предназначено не вам!')
    if 'Гр_нет_' in data_callback:
        data = data_callback.replace('Гр_нет_', '').split('_')
        if str(callback.from_user.id) == data[1]:
            await callback.message.delete()
            await callback.answer(f'Вы отказались быть гражданином')
        else:
            await callback.answer(f'Это предназначено не вам!')
    """🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼ГРАЖДАНИН ДА НЕТ🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼"""

    """🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽ПОКУПКА СТРАНЫ🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽"""
    if 'buy_country_' in data_callback:
        msg_data = [f'Поздравляем нашего президента!!! 🧔\n'
                    f'🛠 Вам доступны следующие команды:\n'
                    f'/get_citizen, Взять гражданина - делаете участника гражданином своей страны (нужно ответить командой на сообщение участника)\n'
                    f'/nalog 1 - устанавливает налог на работу в размере 1% (цифра может быть любая от 0 до 100)\n'
                    f'/mycitizens, Граждане, Мои граждане - покажет список ваших гражданов\n'
                    f'/ccash - управление деньгами в казне\n'
                    f'/cpass, О стране, Моя страна - данные о вашей стране\n'
                    f'/sell_country, Продать страну - продажа страны']
        country = data_callback.replace('buy_country_', '')
        await check_user(callback)
        user_id = callback.from_user.id
        user_info = database.users.find_one({'id': user_id})
        country_info = database.countries.find_one({'country': country})
        if user_info['president_country'] == 'нет' and user_info['cash'] >= country_info['cost'] and country_info[
            'president'] == 0:
            # Вычет денег из баланса
            database.users.update_one({'id': user_id}, {'$set': {'cash': user_info['cash'] - country_info['cost'],
                                                                 'president_country': country,
                                                                 'citizen_country': country}})
            # Страна обрела президента
            database.countries.update_one({'country': country}, {'$set': {'president': user_id}})
            await bot.send_photo(callback.message.chat.id,
                                 caption=f'{await username(callback)} успешно купил страну - {country}! 🌍\n' + ''.join(
                                     msg_data), photo=InputFile(
                    f'{os.getcwd()}/res/country_pic/{country}.png'), parse_mode='HTML')
        elif user_info['cash'] < country_info['cost']:
            await callback.answer(f'Вам нужно ещё {country_info["cost"] - user_info["cash"]:n}$')
        elif user_info["president_country"] != 'нет':
            await callback.answer(f'Вы уже президент страны {user_info["president_country"]}')
        elif country_info['president'] != 0:
            idname = await bot.get_chat(country_info['president'])
            named = quote_html(idname.username)
            await callback.answer('У страны {country} уже есть президент {named}', parse_mode='HTML')
    if 'president' == data_callback:
        await check_user(callback)
        await callback.answer(f'Страна уже имеет президента!')
    """🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼ПОКУПКА СТРАНЫ🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼"""

    """🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽ШКОЛА🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽"""
    if 'school_yes_' in data_callback:
        data = data_callback.replace('school_yes_', '')
        if str(callback.from_user.id) == data:
            user_info = database.users.find_one({'id': callback.from_user.id})
            if user_info['cash'] >= 3000 and user_info['exp'] >= 60:
                # Снятие денег
                database.users.update_one({'id': callback.from_user.id}, {'$set': {'cash': user_info['cash'] - 3000,
                                                                                   'exp': user_info['exp'] - 60}})
                # Статус учебы
                database.education.update_one({'id': callback.from_user.id}, {'$set': {'ucheb': 'Школа',
                                                                                       'class': '1 класс',
                                                                                       'status': 'учусь',
                                                                                       'school': 'да',
                                                                                       'num_question': 0,
                                                                                       'num_teoria': 0
                                                                                       }})
                key = InlineKeyboardMarkup()
                # обновление данных в БД
                educ_info = database.education.find_one({'id': callback.from_user.id})
                database.education.update_one({'id': callback.from_user.id},
                                              {'$set': {'num_teoria': educ_info['num_teoria'] + 1}})
                with open(
                        f'{os.getcwd()}/res/education/{educ_info["class"]}/teor/{educ_info["num_teoria"]}.txt',
                        'r',
                        encoding='utf-8') as f:
                    file = f.readlines()
                    f.close()
                but1 = InlineKeyboardButton('Начать', callback_data='start_teor')
                key.add(but1)
                await bot.send_message(callback.from_user.id, ''.join(file), reply_markup=key)
                await callback.message.delete()
                # await callback.message.edit_text(
                #    f'{await username(callback)}, вы пошли в школу, чтобы начать обучение введите УЧЕБА в личные сообщения бота!',
                #    parse_mode='Markdown')
            elif user_info['cash'] < 3000:
                await callback.message.edit_text(f'{await username(callback)}, у вас недостаточно средств!',
                                                 parse_mode='HTML')
            elif user_info['exp'] < 60:
                await callback.message.edit_text(f'{await username(callback)}, у вас недостаточно опыта!',
                                                 parse_mode='HTML')
        else:
            await callback.answer(f'Это предназначено не вам!')
    if 'school_no_' in data_callback:
        data = data_callback.replace('school_no_', '')
        if str(callback.from_user.id) == data:
            await callback.message.delete()
            await callback.answer(f'Вы отказались от школы!')
        else:
            await callback.answer(f'Это предназначено не вам!')
    """🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼ШКОЛА🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼"""
    """🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽ВУЗ🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽"""
    # Выбор вуза
    if 'vuz_' in data_callback:
        name_job = data_callback.replace('vuz_', '')
        job_info = database.jobs.find_one({'name_job': name_job})
        await callback.message.edit_text(
            f'{await username(callback)}, для обучения в ВУЗе "{name_job}" вам понадобится:\n'
            f'    - {job_info["need_exp"]} опыта\n'
            f'    - {job_info["need_cash"]}$\n'
            f'    - Обучение длится 24 часа\n\n'
            f'❗️ По окончании обучения вы получите возможность работать по профессии {name_job}',
            reply_markup=InlineKeyboardMarkup(1).add(
                InlineKeyboardButton('Начать обучение',
                                     callback_data=f'start_vu_{name_job}'),
                InlineKeyboardButton('Отмена', callback_data='otmena')), parse_mode='HTML')
    # Начало обучения в ВУЗе
    if 'start_vu_' in data_callback:
        name_job = data_callback.replace('start_vu_', '')
        job_info = database.jobs.find_one({'name_job': name_job})

        user_info = database.users.find_one({'id': callback.from_user.id})
        educ_info = database.education.find_one({'id': callback.from_user.id})
        # Если в данный момент нигде не обучаюсь
        if educ_info['ucheb'] == 'нет':
            if user_info['cash'] >= int(job_info['need_cash']) and user_info['exp'] >= int(job_info['need_exp']):
                # обновление данных таблицы
                database.education.update_one({'id': callback.from_user.id}, {'$set': {'ucheb': f'ВУЗ {name_job}'}})
                database.users.update_one({'id': callback.from_user.id},
                                          {'$set': {'cash': user_info['cash'] - int(job_info['need_cash']),
                                                    'exp': user_info['exp'] - int(job_info['need_exp'])}})
                await callback.message.edit_text(
                    f'{await username(callback)},вы начали обучение по профессии {name_job}\n'
                    f'- {job_info["need_exp"]} опыта\n'
                    f'- {job_info["need_cash"]}$\n'
                    f'❗️ До окончания осталось 24 часа', parse_mode='HTML')
                tz = pytz.timezone('Etc/GMT-3')
                res_database.vuz.insert_one({'id': callback.from_user.id,
                                             'job': name_job,
                                             'time': await add_time_min(1440)})
                scheduler.add_job(start_vuz, trigger="date", run_date=await add_time_min(1440), timezone=tz,
                                  id=f'{callback.from_user.id}_vuz',
                                  args=(callback.from_user.id, name_job))
            else:
                await callback.message.edit_text(f'{await username(callback)}, у вас недостаточно средств!',
                                                 parse_mode='HTML')

        else:
            await callback.message.edit_text(f'{await username(callback)}, вы уже обучаетесь', parse_mode='HTML')
    """🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼ВУЗ🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼"""
    """🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽РАБОТА🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽"""
    if 'getjob_' in data_callback:
        job, pressed_user = data_callback.replace('getjob_', '').split('_')
        res_info = res_database.job.find_one({'id': callback.from_user.id})
        user_info = database.users.find_one({'id': callback.from_user.id})
        jobs_citizen = ['Автосборщик', 'Строитель', 'Предприниматель']
        if job in jobs_citizen and user_info['citizen_country'] == 'нет':
            await callback.message.edit_text(f'{await username(callback)}, для начала вам нужно стать гражданином!')
            return
        # Проверка нажал ли тот кто вызвал
        if str(callback.from_user.id)[-2::] != pressed_user:
            await callback.answer(f'Это предназначено не вам!')
            return
            # Если нет данных о работе
        if res_info is None:
            # обновление данных в БД
            database.users.update_one({'id': callback.from_user.id}, {'$set': {'job': job}})
            res_database.job.insert_one({'id': callback.from_user.id,
                                         'time': '0',
                                         'working': False})
            await callback.message.edit_text(f'{await username(callback)}, вы устроились по профессии {job}\n'
                                             f'❗️ Чтобы начать работать напишите - Работа', parse_mode='HTML')
        # Если работает
        elif res_info['working']:
            await callback.message.edit_text('Для начала завершите работу!')
        # Если не работает
        else:
            await callback.message.edit_text(f'{await username(callback)}, вам нужно уволиться\n'
                                             f'❗️ Чтобы уволиться напишите - Уволиться', parse_mode='HTML')
    """🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼РАБОТА🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼"""
    """🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽КЕЙСЫ🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽"""
    if 'Кейсы' in data_callback:
        case_keyboard = InlineKeyboardMarkup(row_width=1)
        buy_little_case_btn = InlineKeyboardButton(text='Маленький кейс за 10 000$', callback_data='Кейс_маленький')
        buy_middle_case_btn = InlineKeyboardButton(text='Средний кейс за 500 000$', callback_data='Кейс_средний')
        buy_big_case_btn = InlineKeyboardButton(text='Большой кейс за 1 500 000$', callback_data='Кейс_большой')
        case_keyboard.add(buy_little_case_btn, buy_middle_case_btn, buy_big_case_btn)
        await callback.message.edit_text(text='Доступны следующие кейсы:', reply_markup=case_keyboard)

    if 'Кейс_' in data_callback:
        if 'Кейс_маленький' in data_callback:
            await callback.message.delete()
            await little_case(callback=callback)
        elif 'Кейс_средний' in data_callback:
            await callback.message.delete()
            await middle_case(callback=callback)
        elif 'Кейс_большой' in data_callback:
            await callback.message.delete()
            await big_case(callback=callback)
    '''🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼КЕЙСЫ🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼'''
    '''marketplace'''
    if 'marketplace_' in data_callback:
        categories_kb = InlineKeyboardMarkup(row_width=1)
        sale_btn = InlineKeyboardButton(text='Продать', callback_data=f'marketsale_{str(callback.from_user.id)[-3::]}')
        buy_btn = InlineKeyboardButton(text='Купить', callback_data=f'marketbuy_{str(callback.from_user.id)[-3::]}')
        seller_btn = InlineKeyboardButton(text='Мои объявления',
                                          callback_data=f'market_my_ads_watch_{str(callback.from_user.id)[-3::]}')
        categories_kb.add(sale_btn, buy_btn, seller_btn)
        await callback.message.edit_text(text='Выберите действие:', reply_markup=categories_kb)

    if 'marketsale_' in data_callback:
        user_id = data_callback.replace('marketsale_', '')
        if str(callback.from_user.id)[-3::] == user_id:
            kb = InlineKeyboardMarkup(row_width=1)
            oil = InlineKeyboardButton(text='Топливо', callback_data='marketseller_sale_oil')
            food = InlineKeyboardButton(text='Еда', callback_data='marketseller_sale_food')
            # car = InlineKeyboardButton(text='Автомобиль', callback_data='marketseller_sale_car')
            back = InlineKeyboardButton(text='Назад', callback_data='marketplace_')
            kb.add(oil, food, back)
            await callback.message.edit_text(text='Выберите товар:', reply_markup=kb)
        else:
            await callback.answer('Это предназначено не вам!')
    # Покупка
    if 'marketbuy_' in data_callback:
        user_id = data_callback.replace('marketbuy_', '')
        if str(callback.from_user.id)[-3::] == user_id:
            kb = InlineKeyboardMarkup(row_width=1)
            oil = InlineKeyboardButton(text='Топливо', callback_data=f'market_buy_oil_{str(callback.from_user.id)[-3::]}')
            food = InlineKeyboardButton(text='Еда', callback_data=f'market_buy_food_{str(callback.from_user.id)[-3::]}')
            # car = InlineKeyboardButton(text='Автомобиль', callback_data='market_buy_car')
            back = InlineKeyboardButton(text='Назад', callback_data='marketplace_')
            kb.add(oil, food, back)
            await callback.message.edit_text(text='Выберите товар:', reply_markup=kb)
        else:
            await callback.answer('Это предназначено не вам!')
    if 'market_buy_' in data_callback:
        product, user_id = data_callback.replace('market_buy_', '').split('_')
        if str(callback.from_user.id)[-3::] == user_id:
            all_ads = list(res_database.marketplace.find({'product': product}))
            if all_ads:
                key = InlineKeyboardMarkup()
                but_nazad = InlineKeyboardButton('◀️',
                                                 callback_data=f'marketbuyer_nazad_{product}_{str(callback.from_user.id)[-3::]}_0')
                but_vpered = InlineKeyboardButton('▶️',
                                                  callback_data=f'marketbuyer_vpered_{product}_{str(callback.from_user.id)[-3::]}_0')
                but_otmena = InlineKeyboardButton('Отмена',
                                                  callback_data=f'marketbuyer_otmena_{product}_{str(callback.from_user.id)[-3::]}')
                but_buy = InlineKeyboardButton('Купить ✅',
                                               callback_data=f'marketbuyer_buy_{product}_{str(callback.from_user.id)[-3::]}_0')
                key.add(but_nazad, but_buy, but_vpered, but_otmena)
                for user in all_ads:
                    isUser = database.users.find_one({'id': user['id']})
                    if isUser is None:
                        res_database.marketplace.delete_one({'id': user['id']})
                        return
                seller_info = database.users.find_one({'id': all_ads[0]['id']})

                await callback.message.edit_text(f'Объявление о продаже от {await username_2(all_ads[0]["id"], seller_info["firstname"])}\n'
                                                 f'Продукт: {product}\n'
                                                 f'Количество: {all_ads[0]["quantity"]}\n'
                                                 f'Цена за данное количество: {all_ads[0]["price"]:n}$\n\n'
                                                 f'Страница 1/{len(all_ads)}', reply_markup=key, parse_mode='HTML')

            else:
                await callback.message.edit_text(f'{await username(callback)}, по данной категории нет объявлений!', parse_mode='HTML')
        else:
            await callback.answer('Это предназначено не вам!')
    if 'marketbuyer_nazad_' in data_callback:
        product, user_id, page = data_callback.replace('marketbuyer_nazad_', '').split('_')
        if str(callback.from_user.id)[-3::] == user_id:
            if int(page) != 0:
                all_ads = list(res_database.marketplace.find({'product': product}))
                key = InlineKeyboardMarkup()
                but_nazad = InlineKeyboardButton('◀️',
                                                 callback_data=f'marketbuyer_nazad_{product}_{str(callback.from_user.id)[-3::]}_{int(page) - 1}')
                but_vpered = InlineKeyboardButton('▶️',
                                                  callback_data=f'marketbuyer_vpered_{product}_{str(callback.from_user.id)[-3::]}_{int(page) - 1}')
                but_otmena = InlineKeyboardButton('Отмена',
                                                  callback_data=f'marketbuyer_otmena_{product}_{str(callback.from_user.id)[-3::]}')
                but_buy = InlineKeyboardButton('Купить ✅',
                                               callback_data=f'marketbuyer_buy_{product}_{str(callback.from_user.id)[-3::]}_{int(page) - 1}')
                key.add(but_nazad, but_buy, but_vpered, but_otmena)
                seller_info = database.users.find_one({'id': all_ads[int(page) - 1]['id']})
                await callback.message.edit_text(
                    f'Объявление о продаже от {await username_2(all_ads[int(page) - 1]["id"], seller_info["firstname"])}\n'
                    f'Продукт: {product}\n'
                    f'Количество: {all_ads[int(page) - 1]["quantity"]}\n'
                    f'Цена за данное количество: {all_ads[int(page) - 1]["price"]:n}$\n\n'
                    f'Страница {int(page)}/{len(all_ads)}', reply_markup=key, parse_mode='HTML')
            else:
                await callback.answer('Это последняя страница!')
        else:
            await callback.answer('Это предназначено не вам!')
    if 'marketbuyer_vpered_' in data_callback:
        product, user_id, page = data_callback.replace('marketbuyer_vpered_', '').split('_')
        all_ads = list(res_database.marketplace.find({'product': product}))
        if str(callback.from_user.id)[-3::] == user_id:
            if int(page) + 1 < len(all_ads):
                key = InlineKeyboardMarkup()
                but_nazad = InlineKeyboardButton('◀️',
                                                 callback_data=f'marketbuyer_nazad_{product}_{str(callback.from_user.id)[-3::]}_{int(page) + 1}')
                but_vpered = InlineKeyboardButton('▶️',
                                                  callback_data=f'marketbuyer_vpered_{product}_{str(callback.from_user.id)[-3::]}_{int(page) + 1}')
                but_otmena = InlineKeyboardButton('Отмена',
                                                  callback_data=f'marketbuyer_otmena_{product}_{str(callback.from_user.id)[-3::]}')
                but_buy = InlineKeyboardButton('Купить ✅',
                                               callback_data=f'marketbuyer_buy_{product}_{str(callback.from_user.id)[-3::]}_{int(page) + 1}')
                key.add(but_nazad, but_buy, but_vpered, but_otmena)
                seller_info = database.users.find_one({'id': all_ads[int(page) + 1]['id']})
                await callback.message.edit_text(
                    f'Объявление о продаже от {await username_2(all_ads[int(page) + 1]["id"], seller_info["firstname"])}\n'
                    f'Продукт: {product}\n'
                    f'Количество: {all_ads[int(page) + 1]["quantity"]}\n'
                    f'Цена за данное количество: {all_ads[int(page) + 1]["price"]:n}$\n\n'
                    f'Страница {int(page) + 2}/{len(all_ads)}', reply_markup=key, parse_mode='HTML')
            else:
                await callback.answer('Это последняя страница!')
        else:
            await callback.answer('Это предназначено не вам!')
    if 'marketbuyer_buy_' in data_callback:
        product, user_id, page = data_callback.replace('marketbuyer_buy_', '').split('_')
        all_ads = list(res_database.marketplace.find({'product': product}))
        if str(callback.from_user.id)[-3::] == user_id:
            user_info = database.users.find_one({'id': callback.from_user.id})
            seller_info = database.users.find_one({'id': all_ads[int(page)]['id']})
            if user_info['id'] == seller_info['id']:
                await callback.message.edit_text(f'{await username(callback)}, вы не можете купить сами у себя!', parse_mode='HTML')
                return
            if user_info['cash'] >= all_ads[int(page)]['price']:
                # Тот кто продавал
                database.users.update_one({'id': seller_info['id']}, {'$set': {'cash': seller_info['cash'] + all_ads[int(page)]['price']}})
                res_database.marketplace.delete_one({'$and': [{'id': seller_info['id']}, {'product': product}]})
                await bot.send_message(seller_info['id'], f'Объявление о продаже от {await username_2(all_ads[int(page)]["id"], seller_info["firstname"])}\n'
                    f'Продукт: {product}\n'
                    f'Количество: {all_ads[int(page)]["quantity"]}\n'
                    f'Цена за данное количество: {all_ads[int(page)]["price"]:n}$\n\n'
                                                          f'Ваш продукт был куплен, средства начислены ✅', parse_mode='HTML')
                # Тот кто купил
                database.users.update_one({'id': callback.from_user.id}, {'$set': {'cash': user_info['cash'] - all_ads[int(page)]['price'],
                                                                                   product: user_info[product] + all_ads[int(page)]['quantity']}})
                await callback.message.edit_text(f'{await username(callback)}, вы успешно приобрели продукт {product} в количестве {all_ads[int(page)]["quantity"]} за {all_ads[int(page)]["price"]:n}$', parse_mode='HTML')
            else:
                await callback.message.edit_text(f'{await username(callback)}, у вас недостаточно средств!', parse_mode='HTML')
        else:
            await callback.answer('Это предназначено не вам!')
    if 'marketbuyer_otmena_' in data_callback:
        product, user_id = data_callback.replace('marketbuyer_otmena_', '').split('_')
        if str(callback.from_user.id)[-3::] == user_id:
            await callback.message.delete()
        else:
            await callback.answer('Это предназначено не вам!')
    # Мои объявления
    if 'market_my_ads_watch_' in data_callback:
        user_id = data_callback.replace('market_my_ads_watch_', '')
        if str(callback.from_user.id)[-3::] == user_id:
            all_ads = list(res_database.marketplace.find({'id': callback.from_user.id}))
            if all_ads:
                key = InlineKeyboardMarkup()
                but_nazad = InlineKeyboardButton('◀️',
                                                 callback_data=f'market_my_ads_nazad_{str(callback.from_user.id)[-3::]}_0')
                but_vpered = InlineKeyboardButton('▶️',
                                                  callback_data=f'market_my_ads_vpered_{str(callback.from_user.id)[-3::]}_0')
                but_otmena = InlineKeyboardButton('Отмена',
                                                  callback_data=f'market_my_ads_otmena_{str(callback.from_user.id)[-3::]}')
                but_buy = InlineKeyboardButton('Убрать ✅',
                                               callback_data=f'market_my_ads_del_{str(callback.from_user.id)[-3::]}_0')
                key.add(but_nazad, but_buy, but_vpered, but_otmena)
                await callback.message.edit_text(f'{await username(callback)}, ваше объявление:\n'
                                                 f'Продукт: {all_ads[0]["product"]}\n'
                                                 f'Количество: {all_ads[0]["quantity"]}\n'
                                                 f'Цена: {all_ads[0]["price"]}\n\n'
                                                 f'Страница: 1/{len(all_ads)}', parse_mode='HTML', reply_markup=key)
            else:
                await callback.message.edit_text(f'{await username(callback)}, у вас нет объявлений!', parse_mode='HTML')
        else:
            await callback.answer('Это предназначено не вам!')
    if 'market_my_ads_nazad_' in data_callback:
        user_id, page = data_callback.replace('market_my_ads_nazad_', '').split('_')

        if str(callback.from_user.id)[-3::] == user_id:
            if int(page) != 0:
                all_ads = list(res_database.marketplace.find({'id': callback.from_user.id}))
                key = InlineKeyboardMarkup()
                but_nazad = InlineKeyboardButton('◀️',
                                                 callback_data=f'market_my_ads_nazad_{str(callback.from_user.id)[-3::]}_{int(page) - 1}')
                but_vpered = InlineKeyboardButton('▶️',
                                                  callback_data=f'market_my_ads_vpered_{str(callback.from_user.id)[-3::]}_{int(page) - 1}')
                but_otmena = InlineKeyboardButton('Отмена',
                                                  callback_data=f'market_my_ads_otmena_{str(callback.from_user.id)[-3::]}')
                but_buy = InlineKeyboardButton('Убрать ✅',
                                               callback_data=f'market_my_ads_del_{str(callback.from_user.id)[-3::]}_{int(page) - 1}')
                key.add(but_nazad, but_buy, but_vpered, but_otmena)
                await callback.message.edit_text(f'{await username(callback)}, ваше объявление:\n'
                                                 f'Продукт: {all_ads[int(page) - 1]["product"]}\n'
                                                 f'Количество: {all_ads[int(page) - 1]["quantity"]}\n'
                                                 f'Цена: {all_ads[int(page) - 1]["price"]}\n\n'
                                                 f'Страница: {int(page)}/{len(all_ads)}', parse_mode='HTML',
                                                 reply_markup=key)
            else:
                await callback.answer('Это последняя страница!')
        else:
            await callback.answer('Это предназначено не вам!')
    if 'market_my_ads_vpered_' in data_callback:
        user_id, page = data_callback.replace('market_my_ads_vpered_', '').split('_')
        all_ads = list(res_database.marketplace.find({'id': callback.from_user.id}))
        if str(callback.from_user.id)[-3::] == user_id:
            if int(page) + 1 < len(all_ads):
                key = InlineKeyboardMarkup()
                but_nazad = InlineKeyboardButton('◀️',
                                                 callback_data=f'market_my_ads_nazad_{str(callback.from_user.id)[-3::]}_{int(page) + 1}')
                but_vpered = InlineKeyboardButton('▶️',
                                                  callback_data=f'market_my_ads_vpered_{str(callback.from_user.id)[-3::]}_{int(page) + 1}')
                but_otmena = InlineKeyboardButton('Отмена',
                                                  callback_data=f'market_my_ads_otmena_{str(callback.from_user.id)[-3::]}')
                but_buy = InlineKeyboardButton('Убрать ✅',
                                               callback_data=f'market_my_ads_del_{str(callback.from_user.id)[-3::]}_{int(page) + 1}')
                key.add(but_nazad, but_buy, but_vpered, but_otmena)
                await callback.message.edit_text(f'{await username(callback)}, ваше объявление:\n'
                                                 f'Продукт: {all_ads[int(page) + 1]["product"]}\n'
                                                 f'Количество: {all_ads[int(page) + 1]["quantity"]}\n'
                                                 f'Цена: {all_ads[int(page) + 1]["price"]}\n\n'
                                                 f'Страница: {int(page) + 2}/{len(all_ads)}', parse_mode='HTML',
                                                 reply_markup=key)
            else:
                await callback.answer('Это последняя страница!')
        else:
            await callback.answer('Это предназначено не вам!')
    if 'market_my_ads_del_' in data_callback:
        user_id, page = data_callback.replace('market_my_ads_del_', '').split('_')

        if str(callback.from_user.id)[-3::] == user_id:
            all_ads = list(res_database.marketplace.find({'id': callback.from_user.id}))
            res_database.marketplace.delete_one(
                {'$and': [{'id': all_ads[int(page)]['id']}, {'product': all_ads[int(page)]['product']}]})

            product = str(all_ads[int(page)]['product'])
            user_info = database.users.find_one({'id': callback.from_user.id})
            database.users.update_one({'id': callback.from_user.id}, {'$set': {product: user_info[product] +
                                                                      all_ads[int(page)]['quantity']}})

            await callback.message.edit_text(f'{await username(callback)}, вы успешно сняли объявление!', parse_mode='HTML')
        else:
            await callback.answer('Это предназначено не вам!')
    if 'market_my_ads_otmena_' in data_callback:
        user_id = data_callback.replace('market_my_ads_otmena_', '')
        if str(callback.from_user.id)[-3::] == user_id:
            await callback.message.delete()
        else:
            await callback.answer('Это предназначено не вам!')

    """🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽ПРОДАЖА БИЗНЕСА🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽"""
    if 'sell_bus_' in data_callback:
        user_id, cost = data_callback.replace('sell_bus_', '').split('_')
        if str(callback.from_user.id)[-3::] == user_id:
            bus_data = database.users_bus.find_one({'boss': callback.from_user.id})
            await callback.message.edit_text(
                f'{await username(callback)}, вы продали бизнес за {round(float(cost), 0)} $:\n'
                f'™️ Название: {bus_data["name"]}\n'
                f'🛠 Что производит: {bus_data["product"]}\n', parse_mode='HTML')
            # начисление денег
            user_info = database.users.find_one({'id': callback.from_user.id})
            database.users.update_one({'id': callback.from_user.id},
                                      {'$set': {user_info['cost'] + round(float(cost), 0)}})
            # удаление бизнеса
            database.users_bus.delete_one({'boss': callback.from_user.id})
            # удаление рабочих
            database.autocreater_work.delete({'boss': callback.from_user.id})
        else:
            await callback.answer('Это предназначено не вам!')
    if 'cancel_' in data_callback:
        id_user = data_callback.split('_')[2]
        if str(callback.from_user.id)[-3::] == id_user:
            await callback.message.delete()
    '''🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼ПРОДАЖА БИЗНЕСА🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼'''
    """🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽ПОКУПКА БИЗНЕСА🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽"""
    if 'buybus_naz_' in data_callback:
        user_id, page = data_callback.replace('buybus_naz_', '').split('_')
        if str(callback.from_user.id)[-3::] == user_id:
            if int(page) != 0:
                user_info = database.users.find_one({'id': callback.from_user.id})
                key = InlineKeyboardMarkup(row_width=3)
                but_nazad = InlineKeyboardButton('◀️',
                                                 callback_data=f'buybus_naz_{str(callback.from_user.id)[-3::]}_{int(page) - 1}')
                but_vpered = InlineKeyboardButton('▶️',
                                                  callback_data=f'buybus_vper_{str(callback.from_user.id)[-3::]}_{int(page) - 1}')
                but_buy = InlineKeyboardButton('Купить 💲',
                                               callback_data=f'buybus_buy_{str(callback.from_user.id)[-3::]}_{int(page) - 1}')
                but_otmena = InlineKeyboardButton('Отмена ❌',
                                                  callback_data=f'buybus_otm_{str(callback.from_user.id)[-3::]}')
                key.add(but_nazad, but_buy, but_vpered, but_otmena)
                bus_data = list(database.businesses.find({'country': user_info['citizen_country']}))
                await callback.message.edit_text(f'Страна производства: {bus_data[int(page) - 1]["country"]}\n'
                                                 f'Что производит: {bus_data[int(page) - 1]["product"]}\n'
                                                 f'🖤 Топлива: {bus_data[int(page) - 1]["oil"]} л\n'
                                                 f'🍔 Еда: {bus_data[int(page) - 1]["food"]} кг\n'
                                                 f'💵 Цена: {bus_data[int(page) - 1]["cost"]} $\n\n'
                                                 f'Страница {int(page)}/{len(bus_data)}', reply_markup=key)
            else:
                await callback.answer('Это последняя страница')
        else:
            await callback.answer('Это предназначено не вам!')
    if 'buybus_vper_' in data_callback:
        user_id, page = data_callback.replace('buybus_vper_', '').split('_')
        if str(callback.from_user.id)[-3::] == user_id:
            user_info = database.users.find_one({'id': callback.from_user.id})
            bus_data = list(database.businesses.find({'country': user_info['citizen_country']}))
            if int(page) + 1 != len(bus_data):
                key = InlineKeyboardMarkup(row_width=3)
                but_nazad = InlineKeyboardButton('◀️',
                                                 callback_data=f'buybus_naz_{str(callback.from_user.id)[-3::]}_{int(page) + 1}')
                but_vpered = InlineKeyboardButton('▶️',
                                                  callback_data=f'buybus_vper_{str(callback.from_user.id)[-3::]}_{int(page) + 1}')
                but_buy = InlineKeyboardButton('Купить 💲',
                                               callback_data=f'buybus_buy_{str(callback.from_user.id)[-3::]}_{int(page) + 1}')
                but_otmena = InlineKeyboardButton('Отмена ❌',
                                                  callback_data=f'buybus_otm_{str(callback.from_user.id)[-3::]}')
                key.add(but_nazad, but_buy, but_vpered, but_otmena)

                await callback.message.edit_text(f'Страна производства: {bus_data[int(page) + 1]["country"]}\n'
                                                 f'Что производит: {bus_data[int(page) + 1]["product"]}\n'
                                                 f'🖤 Топлива: {bus_data[int(page) + 1]["oil"]} л\n'
                                                 f'🍔 Еда: {bus_data[int(page) + 1]["food"]} кг\n'
                                                 f'💵 Цена: {bus_data[int(page) + 1]["cost"]} $\n\n'
                                                 f'Страница {int(page) + 2}/{len(bus_data)}', reply_markup=key)
            else:
                await callback.answer('Это последняя страница')
        else:
            await callback.answer('Это предназначено не вам!')
    if 'buybus_buy_' in data_callback:
        user_id, page = data_callback.replace('buybus_buy_', '').split('_')
        if str(callback.from_user.id)[-3::] == user_id:
            user_info = database.users.find_one({'id': callback.from_user.id})
            bus_data = list(database.businesses.find({'country': user_info['citizen_country']}))
            # Проверка ресурсов
            if user_info['cash'] < bus_data[int(page)]['cost']:
                await callback.message.edit_text(
                    f'{await username(callback)}, вам не хватает {bus_data[int(page)]["cost"] - user_info["cash"]} $',
                    parse_mode='HTML')
                return
            if user_info['oil'] < bus_data[int(page)]['oil']:
                await callback.message.edit_text(
                    f'{await username(callback)}, вам не хватает {bus_data[int(page)]["oil"] - user_info["oil"]} 🖤',
                    parse_mode='HTML')
                return
            if user_info['food'] < bus_data[int(page)]['food']:
                await callback.message.edit_text(
                    f'{await username(callback)}, вам не хватает {bus_data[int(page)]["food"] - user_info["food"]} 🍔',
                    parse_mode='HTML')
                return
            # Снятие ресурсов
            database.users.update_one({'id': callback.from_user.id}, {'$set': {
                'cash': user_info['cash'] - bus_data[int(page)]['cost'],
                'oil': user_info['oil'] - bus_data[int(page)]['oil'],
                'food': user_info['food'] - bus_data[int(page)]['food']
            }})
            # Запись страны в user_bus
            database.users_bus.insert_one({'boss': callback.from_user.id,
                                           'country': bus_data[int(page)]['country'],
                                           'name': bus_data[int(page)]['name'],
                                           'product': bus_data[int(page)]['product'],
                                           'need_builder': bus_data[int(page)]['need_builder'],
                                           'oil': bus_data[int(page)]['oil'],
                                           'food': bus_data[int(page)]['food'],
                                           'cost': bus_data[int(page)]['cost'],
                                           'work_place': bus_data[int(page)]['work_place'],
                                           'time_to_create': bus_data[int(page)]['time_to_create'],
                                           'status': 'buy',
                                           'bpay': 0}
                                          )
            await callback.message.edit_text(
                f'{await username(callback)}, вы успешно приобрели бизнес {bus_data[int(page)]["name"]} {bus_data[int(page)]["product"]}',
                parse_mode='HTML')

        else:
            await callback.answer('Это предназначено не вам!')
    if 'buybus_otm_' in data_callback:
        user_id = data_callback.replace('buybus_otm_', '').split('_')
        if str(callback.from_user.id)[-3::] == user_id:
            await callback.message.delete()
        else:
            await callback.answer('Это предназначено не вам!')
    '''🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼ПОКУПКА БИЗНЕСА🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼'''
    """🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽ОТМЕНА СТРОИТЕЛЬСТВА🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽"""
    if 'cancel_bus_yes_' in data_callback:
        user_id = data_callback.replace('cancel_bus_yes_', '').split('_')
        if user_id == str(callback.from_user.id)[-3::]:
            bus_info = database.users_bus.find_one({'boss': callback.from_user.id})
            boss_info = database.users.find_one({'id': callback.from_user.id})
            database.users.update_one({'id': callback.from_user.id},
                                      {'$set': {'cash': boss_info['cash'] + round(float(bus_info["bpay"] * 0.5)),
                                                'oil': boss_info['oil'] + bus_info['oil'] * 0.5,
                                                'food': boss_info['food'] + bus_info['food'] * 0.5}})
            builders_info = list(database.builders_work.find({'boss': callback.from_user.id}))
            # Выдача денег строителям\расформирование их
            for builder in builders_info:
                builder_info = database.users.find_one({'id': builder['builder']})
                job_info = database.jobs.find_one({'name_job': builder_info['job']})
                database.users.update_one({'id': builders_info['builder']},
                                          {'$set': {'cash': builder_info['cash'] + round(float(bus_info["bpay"] * 0.5)),
                                                    'exp': builder_info['exp'] + job_info['exp_for_job']}})
                database.builders_work.delete_one({'builder': builder['builder']})
                await bot.send_message(builder['builder'],
                                       f'{await username_2(builder_info["id"], builders_info["firstname"])}, вы получили вознаграждение за стройку объекта {bus_info["name"]} {bus_info["product"]}\n'
                                       f'❗️ Стройка была прервана работодателем\n'
                                       f'💵 +{round(float(bus_info["bpay"] * 0.5))}\n'
                                       f'🏵 +{job_info["exp_for_job"]}', parse_mode='HTML')
            res_database.build_bus.delete_one({'boss': callback.from_user.id})
            scheduler.remove_job(f'{callback.from_user.id}_build')
            database.users_bus.delete_one({'boss': callback.from_user.id})
            await callback.message.edit_text(f'{await username(callback)}, вы успешно прервали стройку!\n'
                                             f'❗️ Все средства были вернуты на 50%', parse_mode='HTML')
        else:
            await callback.answer('Это предназначено не вам!')
    if 'cancel_bus_no_' in data_callback:
        user_id = data_callback.replace('cancel_bus_yes_', '').split('_')
        if user_id == str(callback.from_user.id)[-3::]:
            await callback.message.delete()
        else:
            await callback.answer('Это предназначено не вам!')
    '''🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼ОТМЕНА СТРОИТЕЛЬСТВА🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼'''
    """🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽ПОИСК СТРОЙКИ ДЛЯ СТРОИТЕЛЯ🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽"""
    if 'build_naz_' in data_callback:
        user_id, page = data_callback.replace('build_naz_', '').split('_')
        if str(callback.from_user.id)[-3::] == user_id:
            if int(page) != 0:
                user_info = database.users.find_one({'id': callback.from_user.id})
                key = InlineKeyboardMarkup(row_width=3)
                but_nazad = InlineKeyboardButton('◀️',
                                                 callback_data=f'build_naz_{str(callback.from_user.id)[-3::]}_{int(page) - 1}')
                but_vpered = InlineKeyboardButton('▶️',
                                                  callback_data=f'build_vper_{str(callback.from_user.id)[-3::]}_{int(page) - 1}')
                but_ustroitsya = InlineKeyboardButton('Устроиться ✅',
                                                      callback_data=f'build_ustr_{str(callback.from_user.id)[-3::]}_{int(page) - 1}')
                but_otmena = InlineKeyboardButton('Отмена ❌',
                                                  callback_data=f'build_otm_{str(callback.from_user.id)[-3::]}')
                key.add(but_nazad, but_ustroitsya, but_vpered, but_otmena)
                all_building = list(database.users_bus.find(
                    {'$and': [{'status': 'need_builders'}, {'country': user_info['citizen_country']}]}))
                all_builders = list(database.builders_work.find({'boss': all_building[int(page) - 1]['boss']}))
                await callback.message.edit_text('Бизнесы в режиме ожидания:'
                                                 f'{all_building[int(page) - 1]["name"]} {all_building[int(page) - 1]["product"]}\n'
                                                 f'Плата за стройку: {all_building[int(page) - 1]["bpay"]}\n'
                                                 f'Строителей на объекте: {len(all_builders)} из {all_building[int(page) - 1]["need_builder"]}\n\n'
                                                 f'Страница {int(page)}/{len(all_building)}', reply_markup=key)
            else:
                await callback.answer('Это последняя страница')
        else:
            await callback.answer('Это предназначено не вам!')
    if 'build_vper_' in data_callback:
        user_id, page = data_callback.replace('build_vper_', '').split('_')
        if str(callback.from_user.id)[-3::] == user_id:
            user_info = database.users.find_one({'id': callback.from_user.id})
            all_building = list(database.users_bus.find(
                {'$and': [{'status': 'need_builders'}, {'country': user_info['citizen_country']}]}))
            if int(page) + 1 != len(all_building):
                key = InlineKeyboardMarkup(row_width=3)
                but_nazad = InlineKeyboardButton('◀️',
                                                 callback_data=f'build_naz_{str(callback.from_user.id)[-3::]}_{int(page) + 1}')
                but_vpered = InlineKeyboardButton('▶️',
                                                  callback_data=f'build_vper_{str(callback.from_user.id)[-3::]}_{int(page) + 1}')
                but_ustroitsya = InlineKeyboardButton('Устроиться ✅',
                                                      callback_data=f'build_ustr_{str(callback.from_user.id)[-3::]}_{int(page) + 1}')
                but_otmena = InlineKeyboardButton('Отмена ❌',
                                                  callback_data=f'build_otm_{str(callback.from_user.id)[-3::]}')
                key.add(but_nazad, but_ustroitsya, but_vpered, but_otmena)
                all_builders = list(database.builders_work.find({'boss': all_building[int(page) + 1]['boss']}))
                await callback.message.edit_text('Бизнесы в режиме ожидания:'
                                                 f'{all_building[int(page) + 1]["name"]} {all_building[int(page) + 1]["product"]}\n'
                                                 f'Плата за стройку: {all_building[int(page) + 1]["bpay"]}\n'
                                                 f'Строителей на объекте: {len(all_builders)} из {all_building[int(page) + 1]["need_builder"]}\n\n'
                                                 f'Страница {int(page) + 2}/{len(all_building)}', reply_markup=key)
            else:
                await callback.answer('Это последняя страница')
        else:
            await callback.answer('Это предназначено не вам!')
    if 'build_ustr_' in data_callback:
        user_id, page = data_callback.replace('build_ustr_', '').split('_')
        if str(callback.from_user.id)[-3::] == user_id:
            user_info = database.users.find_one({'id': callback.from_user.id})
            all_building = list(database.users_bus.find(
                {'$and': [{'status': 'need_builders'}, {'country': user_info['citizen_country']}]}))
            all_builders = list(database.builders_work.find({'boss': all_building[int(page)]['boss']}))
            if all_building[int(page)]['need_builder'] <= len(all_builders):
                key = InlineKeyboardMarkup(row_width=3)
                but_nazad = InlineKeyboardButton('◀️',
                                                 callback_data=f'build_naz_{str(callback.from_user.id)[-3::]}_{int(page)}')
                but_vpered = InlineKeyboardButton('▶️',
                                                  callback_data=f'build_vper_{str(callback.from_user.id)[-3::]}_{int(page)}')
                but_ustroitsya = InlineKeyboardButton('Устроиться ✅',
                                                      callback_data=f'build_ustr_{str(callback.from_user.id)[-3::]}_{int(page)}')
                but_otmena = InlineKeyboardButton('Отмена ❌',
                                                  callback_data=f'build_otm_{str(callback.from_user.id)[-3::]}')
                key.add(but_nazad, but_ustroitsya, but_vpered, but_otmena)
                all_builders = list(database.builders_work.find({'boss': all_building[int(page)]['boss']}))
                await callback.message.edit_text('Бизнесы в режиме ожидания:'
                                                 f'{all_building[int(page)]["name"]} {all_building[int(page)]["product"]}\n'
                                                 f'Плата за стройку: {all_building[int(page)]["bpay"]}\n'
                                                 f'Строителей на объекте: {len(all_builders)} из {all_building[int(page)]["need_builder"]}\n'
                                                 f'❗️ На этом объекте достигнуто максимальное количество'
                                                 f'Страница {int(page) + 1}/{len(all_building)}', reply_markup=key)
                return
            database.builders_work.insert_one({'boss': all_building[int(page)]['boss'],
                                               'builder': callback.from_user.id})
            await callback.message.edit_text(
                f'{await username(callback)}, вы успешно устроились на объект {all_building[int(page)]["name"]} {all_building[int(page)]["product"]}', parse_mode='HTML')
        else:
            await callback.answer('Это предназначено не вам!')
    if 'build_otm_' in data_callback:
        user_id = data_callback.replace('build_otm_', '').split('_')
        if str(callback.from_user.id)[-3::] == user_id:
            await callback.message.delete()
        else:
            await callback.answer('Это предназначено не вам!')
    '''🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼ПОИСК СТРОЙКИ ДЛЯ СТРОИТЕЛЯ🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼'''
    """🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽УЙТИ СО СТРОЙКИ🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽"""
    if 'leave_build_yes_' in data_callback:
        user_id = data_callback.replace('leave_build_yes_', '')
        if user_id == str(callback.from_user.id)[-3::]:
            bus_info = database.users_bus.find_one(
                {'boss': database.builders_work({'builder': callback.from_user.id})['boss']})
            database.builders_work.delete_one({'builder': callback.from_user.id})
            await callback.message.edit_text(
                f'{await username(callback.from_user.id)}, покинул стройку бизнеса {bus_info["name"]} {bus_info["product"]}')
        else:
            await callback.answer('Это предназначено не вам!')
    if 'leave_build_no_' in data_callback:
        user_id = data_callback.replace('leave_build_no_', '')
        if user_id == str(callback.from_user.id)[-3::]:
            await callback.message.delete()
        else:
            await callback.answer('Это предназначено не вам!')
    '''🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼УЙТИ СО СТРОЙКИ🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼'''
    """🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽ПОИСК РАБОТЫ АВТОСБОРЩИК🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽"""
    if 'creater_nazad_' in data_callback:
        user_id, page = data_callback.replace('creater_nazad_', '').split('_')
        if str(callback.from_user.id)[-3::] == user_id:
            if int(page) != 0:
                user_info = database.users.find_one({'id': callback.from_user.id})
                all_bus = list(database.users_bus.find(
                    {'$and': [{'name': 'Сборка авто'}, {'status': 'work'}, {'country': user_info['citizen_country']}]}))
                new_list_bus = []
                for bus in all_bus:
                    all_autocreaters = list(database.autocreater_work.find({'boss': bus['boss']}))
                    if len(all_autocreaters) < bus['work_place']:
                        new_list_bus.append(bus)
                key = InlineKeyboardMarkup()
                but_nazad = InlineKeyboardButton('◀️',
                                                 callback_data=f'creater_nazad_{str(callback.from_user.id)[-3::]}_{int(page) - 1}')
                but_vpered = InlineKeyboardButton('▶️',
                                                  callback_data=f'creater_vper_{str(callback.from_user.id)[-3::]}_{int(page) - 1}')
                accept = InlineKeyboardButton('Устроиться ✅',
                                              callback_data=f'creater_ustr_{str(callback.from_user.id)[-3::]}_{int(page) - 1}')
                otmena = InlineKeyboardButton('Отмена ❌', callback_data=f'creater_otmena_')
                key.add(but_nazad, accept, but_vpered, otmena)
                await callback.message.edit_text(
                    f'Бизнес: {new_list_bus[int(page) - 1]["name"]} {new_list_bus[int(page) - 1]["product"]}\n'
                    f'Владелец: {await username(callback)}\n'
                    f'Автосборщиков: {len(list(database.autocreater_work.find({"boss": new_list_bus[int(page) - 1]["boss"]})))}/{new_list_bus[int(page) - 1]["work_place"]}\n\n'
                    f'Страница: {int(page)}/{len(new_list_bus)}', reply_markup=key, parse_mode='HTML')
            else:
                await callback.answer('Это последняя страница')
        else:
            await callback.answer('Это предназначено не вам!')
    if 'creater_vper_' in data_callback:
        user_id, page = data_callback.replace('creater_vper_', '').split('_')
        if str(callback.from_user.id)[-3::] == user_id:
            user_info = database.users.find_one({'id': callback.from_user.id})
            all_bus = list(database.users_bus.find(
                {'$and': [{'name': 'Сборка авто'}, {'status': 'work'}, {'country': user_info['citizen_country']}]}))
            new_list_bus = []
            for bus in all_bus:
                all_autocreaters = list(database.autocreater_work.find({'boss': bus['boss']}))
                if len(all_autocreaters) < bus['work_place']:
                    new_list_bus.append(bus)
            if int(page) + 1 != len(new_list_bus):
                key = InlineKeyboardMarkup()
                but_nazad = InlineKeyboardButton('◀️',
                                                 callback_data=f'creater_nazad_{str(callback.from_user.id)[-3::]}_{int(page) + 1}')
                but_vpered = InlineKeyboardButton('▶️',
                                                  callback_data=f'creater_vper_{str(callback.from_user.id)[-3::]}_{int(page) + 1}')
                accept = InlineKeyboardButton('Устроиться ✅',
                                              callback_data=f'creater_ustr_{str(callback.from_user.id)[-3::]}_{int(page) + 1}')
                otmena = InlineKeyboardButton('Отмена ❌', callback_data=f'creater_otmena_')
                key.add(but_nazad, accept, but_vpered, otmena)
                await callback.message.edit_text(
                    f'Бизнес: {new_list_bus[int(page) + 1]["name"]} {new_list_bus[int(page) + 1]["product"]}\n'
                    f'Владелец: {await username(callback)}\n'
                    f'Автосборщиков: {len(list(database.autocreater_work.find({"boss": new_list_bus[int(page) + 1]["boss"]})))}/{new_list_bus[int(page) + 1]["work_place"]}\n\n'
                    f'Страница: {int(page) + 2}/{len(new_list_bus)}', reply_markup=key, parse_mode='HTML')
            else:
                await callback.answer('Это последняя страница')
        else:
            await callback.answer('Это предназначено не вам!')
    if 'creater_ustr_' in data_callback:
        user_id, page = data_callback.replace('creater_ustr_', '').split('_')
        if str(callback.from_user.id)[-3::] == user_id:
            user_info = database.users.find_one({'id': callback.from_user.id})
            all_bus = list(database.users_bus.find(
                {'$and': [{'name': 'Сборка авто'}, {'status': 'work'}, {'country': user_info['citizen_country']}]}))
            new_list_bus = []
            for bus in all_bus:
                all_autocreaters = list(database.autocreater_work.find({'boss': bus['boss']}))
                if len(all_autocreaters) < bus['work_place']:
                    new_list_bus.append(bus)
            database.autocreater_work.insert_one({'boss': new_list_bus[int(page)]["boss"],
                                                  'creater': callback.from_user.id})
            await callback.message.edit_text(
                f'{await username(callback)}, вы успешно устроились на {new_list_bus[int(page)]["name"]} {new_list_bus[int(page)]["product"]}', parse_mode='HTML')
        else:
            await callback.answer('Это предназначено не вам!')
    if 'creater_otmena' in data_callback:
        user_id = data_callback.replace('creater_otmena', '').split('_')
        if str(callback.from_user.id)[-3::] == user_id:
            await callback.message.delete()
        else:
            await callback.answer('Это предназначено не вам!')
    '''🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼ПОИСК РАБОТЫ АВТОСБОРЩИК🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼'''
    await bot.answer_callback_query(callback.id)


"""🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽"""
'''🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼'''


def reg_all(dp: Dispatcher):
    dp.register_callback_query_handler(otmena, text='otmena')
    dp.register_callback_query_handler(all)
