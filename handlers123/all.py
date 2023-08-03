import asyncio
import json
import os
import random

from bot import Dispatcher, check_user, database, types, InlineKeyboardButton, InlineKeyboardMarkup, \
    InputFile, quote_html, username, username_2, pytz, scheduler, add_time_min, res_database, start_vuz
from cases import Database, Cases, little_case, middle_case, big_case
from create_bot import bot


# Отмена
async def otmena(callback: types.CallbackQuery):
    await callback.message.delete()


async def all(callback: types.CallbackQuery):
    await check_user(callback)
    user_id = callback.from_user.id
    data_callback = callback.data
    path = os.getcwd()
    print(data_callback)
    # Покупка машины
    if 'shop_' in data_callback:
        data_callback = str(data_callback.replace('shop_', ''))
        user_info = database.users.find_one({'id': user_id})
        car_info = database.cars.find_one({'name_car': data_callback})
        if car_info['count'] == 0:
            await callback.message.edit_text(f'{await username(callback)}, {car_info["name_car"]} нет в наличии!', parse_mode='HTML')
            return
        if user_info['cash'] >= car_info['cost']:
            count_user_car = database.users_cars.find_one({'$and': [{'id': user_id}, {'car': car_info['name_car']}]})
            if count_user_car is None:
                database.users_cars.insert_one({'id': user_id,
                                                'car': car_info['name_car'],
                                                'fuel_per_hour': car_info['fuel_per_hour'],
                                                'save_job_time': car_info['save_job_time'],
                                                'count': 1,
                                                'active': False})
                # -1 из наличия
                database.cars.update_one({'name_car': data_callback}, {'$set': {'count': car_info['count'] - 1}})
                # Снятие денег с баланса
                database.cars.update_one({'users': user_id}, {'$set': {'cash': user_info['cash'] - car_info['cost']}})
                # Зачисление денег на баланс государства
                country_info = database.countries.find_one({'country': car_info['country']})
                database.countries.update_one({'country': car_info['country']},
                                              {'$set': {'cash': country_info['cash'] + car_info['cost']}})
                await bot.send_photo(callback.message.chat.id,
                                     caption=f'{await username(callback)}, успешно приобрел машину!',
                                     photo=InputFile(
                                         f'{os.getcwd()}/res/cars_pic/{car_info["name_car"]} {car_info["color"]}.png'), parse_mode='HTML')
            else:
                # Добавление машины пользователю
                database.users_cars.update_one({'id': user_id, 'car': car_info['name_car']},
                                               {'$set': {'count': count_user_car['count'] + 1}})
                # Удалении одной машины из бд
                database.cars.update_one({'name_car': data_callback}, {'$set': {'count': car_info['count'] - 1}})
                # Снятие денег с покупателя
                database.cars.update_one({'users': user_id}, {'$set': {'cash': user_info['cash'] - car_info['cost']}})
                # Зачисление денег на баланс государства
                country_info = database.countries.find_one({'country': car_info['country']})
                database.countries.update_one({'country': car_info['country']},
                                              {'$set': {'cash': country_info['cash'] + car_info['cost']}})
                await bot.send_photo(callback.message.chat.id,
                                     caption=f'{await username(callback)}, успешно приобрел машину!',
                                     photo=InputFile(
                                         f'{os.getcwd()}/res/cars_pic/{car_info["name_car"]} {car_info["color"]}.png'), parse_mode='HTML')

        else:
            await bot.send_message(callback.message.chat.id,
                                   text=f'{await username(callback)}, у вас недостаточно средств!', parse_mode='HTML')
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
            with open(f'{os.getcwd()}/res/countries.txt', 'r', encoding='utf-8') as f:
                while True:
                    line = f.readline()
                    if not line:
                        break
                    else:
                        countries_settings = line.replace('\n', '').split('.')
                        if countries_settings[0] == data[1]:
                            database.countries.update_one({'country': data[1]}, {'$set': {
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
                            }})
                            break
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
    if 'Кейсы' in data_callback:
        case_keyboard = InlineKeyboardMarkup(row_width=1)
        buy_little_case_btn = InlineKeyboardButton(text='Маленький кейс за 10000$', callback_data='Кейс_маленький')
        buy_middle_case_btn = InlineKeyboardButton(text='Средний кейс за 100000$', callback_data='Кейс_средний')
        buy_big_case_btn = InlineKeyboardButton(text='Большой кейс за 150000$', callback_data='Кейс_большой')
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
        await callback.answer(text='ждите, скоро будет')
    await bot.answer_callback_query(callback.id)










def reg_all(dp: Dispatcher):
    dp.register_callback_query_handler(otmena, text='otmena')
    dp.register_callback_query_handler(all)

