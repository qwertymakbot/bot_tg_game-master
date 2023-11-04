from bot import check_user, bot, Dispatcher, parser, database, InlineKeyboardButton, InlineKeyboardMarkup, username_2, username
import pytz
import datetime
import os
import json
import asyncio

# Создать игру
async def create_game(message):
    await check_user(message)
    user_info = database.users.find_one({'id': message.from_user.id})
    if user_info['job'] == 'Крупье':
        try:
            path = os.getcwd()
            with open(f'{path}/game/casino/games/{message.chat.id}_{message.from_user.id}.json', 'r',
                      encoding='utf-8') as f:
                data = json.load(f)
                f.close()
                username = []
                for i in data['игроки']:
                    userna = database.users.find_one({'id': i})
                    if userna is not None:
                        username.append(f'@{userna["username"]} ')
                try:
                    # Текущее время
                    tz = pytz.timezone('Etc/GMT-3')
                    now_time = tz.localize(datetime.datetime.now())
                    end_time = data['конец_игры']
                    end_time = parser.parse(str(end_time))
                    timeleft = end_time - now_time
                    timeleft = str(timeleft).split('.')
                    timeleft = str(timeleft[0]).split(':')
                    timeleft = datetime.timedelta(hours=int(timeleft[0]), minutes=int(timeleft[1]),
                                                  seconds=int(timeleft[2]))

                    await message.answer(f'@{message.from_user.username}, у вас уже есть активная игра!\n'
                                         f'Игроки: {"".join(username)}\n'
                                         f'Количество: {len(username)} из {data["макс_игроков"]}\n'
                                         f'Ставка стола: {data["ставка"]}$\n'
                                         f'Осталось играть: {timeleft}')
                except:
                    # игра больше не существет
                    os.remove(f'{path}/game/casino/games/{message.chat.id}_{message.from_user.id}.json')
                    # вернуть ставки обратно если будут
                    arr = next(os.walk(f'{os.getcwd()}/game/casino/games'))[2]
                    if f'{message.chat.id}_{message.from_user.id}.json' in arr:
                        with open(
                                f'{os.getcwd()}/game/casino/games/{message.chat.id}_{message.from_user.id}.json',
                                'r', encoding='utf-8') as f:
                            data = json.load(f)
                            f.close()
                            stavki = data['ставки']

                            for user in stavki:
                                user_id = list(user.keys())[0]
                                us_info = database.users.find_one({'id': user_id})
                                stavki_user = user[user_id]
                                for stavka in list(stavki_user.keys()):
                                    database.users.update_one({'id': user_id}, {'$set': us_info['cash'] + stavki_user[stavka]})
                    await bot.send_message(message.chat.id, 'Напишите создать игру!')
        except:
            path = os.getcwd()
            with open(f'{path}/game/casino/games/{message.chat.id}_{message.from_user.id}.json', 'w',
                      encoding='utf-8') as f:
                data = {}
                data['игроки'] = []
                data['макс_игроков'] = 6
                data['мин_игроков'] = 2
                data['актив_игры'] = 30
                data['ставка'] = 10
                data['запущ_рулетка'] = False
                data['ставки'] = []
                # Текущее время
                tz = pytz.timezone('Etc/GMT-3')
                now_time = tz.localize(datetime.datetime.now())
                data['конец_игры'] = str(now_time + datetime.timedelta(minutes=data['актив_игры']))
                json.dump(data, f)
                f.close()
                await message.answer(f'@{message.from_user.username}, создал игру РУЛЕТКА!\n'
                                     f'Максимум игроков: {data["макс_игроков"]}\n'
                                     f'Текущая ставка стола {data["ставка"]}$ (изменить ставку /stavka 100)\n'
                                     f'❗️ Чтобы присоединиться введите Рулетка')
                await asyncio.sleep(data['актив_игры'] * 60)
                os.remove(f'{path}/game/casino/games/{message.chat.id}_{message.from_user.id}.json')
                # вернуть ставки обратно если будут
                arr = next(os.walk(f'{os.getcwd()}/game/casino/games'))[2]
                if f'{message.chat.id}_{message.from_user.id}.json' in arr:
                    with open(
                            f'{os.getcwd()}/game/casino/games/{message.chat.id}_{message.from_user.id}.json',
                            'r', encoding='utf-8') as f:
                        data = json.load(f)
                        f.close()
                        stavki = data['ставки']

                        for user in stavki:
                            user_id = list(user.keys())[0]
                            us_info = database.users.find_one({'id': user_id})
                            stavki_user = user[user_id]
                            for stavka in list(stavki_user.keys()):
                                database.users.update_one({'id': user_id},
                                                          {'$set': us_info['cash'] + stavki_user[stavka]})
                await message.answer(f'@{message.from_user.username}, ваша игра была закончена!\n'
                                     f'❗️ Если хотите ещё, создайте новую игру комадой Создать игру')
    else:
        await message.answer(f'@{message.from_user.username}, данная команда вам недоступна!')

# /stavka 100 Изменить ставку стола
async def stavka(message):
    await check_user(message)
    path = os.getcwd()
    user_info = database.users.find_one({'id': message.from_user.id})
    if user_info['job'] == 'Крупье':
        stavk = message.get_args().split()
        try:
            stavk = int(stavk[0])
            try:
                with open(f'{path}/game/casino/games/{message.chat.id}_{message.from_user.id}.json', 'r',
                          encoding='utf-8') as f:
                    data = json.load(f)
                    f.close()
                    data['ставка'] = stavk
                    with open(f'{path}/game/casino/games/{message.chat.id}_{message.from_user.id}.json', 'w',
                              encoding='utf-8') as f:
                        json.dump(data, f)
                        f.close()
                        await message.answer(
                            f'@{message.from_user.username}, текущая ставка стола изменена на {stavk}$\n'
                            f'❗️ Нажмите на кнопку обновить, чтобы ставка обновилась, если вы начали игру!')
            except:
                await message.answer(f'@{message.from_user.username}, у вас нет активных игр!')
        except:
            await message.answer(f'@{message.from_user.username}, ставка введена некорректно (/stavka 100)')

# Рулетка
async def rulette(message):
    await check_user(message)
    path = os.getcwd()
    user_info = database.users.find_one({'id': message.from_user.id})
    if user_info['job'] == 'Крупье':
        # Проверка игры на актуальность
        try:
            path = os.getcwd()
            with open(f'{path}/game/casino/games/{message.chat.id}_{message.from_user.id}.json', 'r',
                      encoding='utf-8') as f:
                data = json.load(f)
                f.close()
        except:
            await bot.send_message(message.chat.id, f'@{message.from_user.username}, для начала создайте игру, командой Создать игру')
            return
        try:
            # Текущее время
            tz = pytz.timezone('Etc/GMT-3')
            now_time = tz.localize(datetime.datetime.now())
            end_time = data['конец_игры']
            end_time = parser.parse(str(end_time))
            timeleft = end_time - now_time
            timeleft = str(timeleft).split('.')
            timeleft = str(timeleft[0]).split(':')
            hour24 = datetime.timedelta(hours=24, minutes=0, seconds=0)
            timeleft = datetime.timedelta(hours=int(timeleft[0]), minutes=int(timeleft[1]),
                                          seconds=int(timeleft[2]))
        except:
            # игра больше не существет
            os.remove(f'{path}/game/casino/games/{message.chat.id}_{message.from_user.id}.json')
            # вернуть ставки обратно если будут
            arr = next(os.walk(f'{os.getcwd()}/game/casino/games'))[2]
            if f'{message.chat.id}_{message.from_user.id}.json' in arr:
                with open(
                        f'{os.getcwd()}/game/casino/games/{message.chat.id}_{message.from_user.id}.json',
                        'r', encoding='utf-8') as f:
                    data = json.load(f)
                    f.close()
                    stavki = data['ставки']

                    for user in stavki:
                        user_id = list(user.keys())[0]
                        us_info = database.users.find_one({'id': user_id})
                        stavki_user = user[user_id]
                        for stavka in list(stavki_user.keys()):
                            database.users.update_one({'id': user_id},
                                                      {'$set': us_info['cash'] + stavki_user[stavka]})
            await bot.send_message(message.chat.id, 'Напишите создать игру!')
            return

        # Вывод сделаных ставок
        arr = next(os.walk(f'{path}/game/casino/games'))[2]
        num = 0
        for i in arr:
            if str(message.chat.id) in i:
                num += 1
                if f'{message.chat.id}_{message.from_user.id}.json' == i:
                    key = InlineKeyboardMarkup(row_width=3)
                    num_but1 = 1
                    for a in range(0, 24):
                        if num_but1 % 2 == 0:
                            but1 = InlineKeyboardButton(f'{num_but1} 🔴',
                                                        callback_data=f'ruletke_choice_{num_but1}_red_{message.chat.id}_{message.from_user.id}')
                            key.insert(but1)
                        else:
                            but1 = InlineKeyboardButton(f'{num_but1} ⚫️',
                                                        callback_data=f'ruletke_choice_{num_but1}_black_{message.chat.id}_{message.from_user.id}')
                            key.insert(but1)
                        num_but1 += 1
                    but0 = InlineKeyboardButton(f'0 🟢',
                                                callback_data=f'ruletke_choice_0_green_{message.chat.id}_{message.from_user.id}')
                    key.add(but0)
                    # На красное
                    red = InlineKeyboardButton(f'На красное 🔴',
                                               callback_data=f'ruletke_only_красное_{message.chat.id}_{message.from_user.id}')
                    # На черное
                    black = InlineKeyboardButton(f'На черное ⚫️',
                                                 callback_data=f'ruletke_only_черное_{message.chat.id}_{message.from_user.id}')
                    key.add(red, black)
                    # все На красное
                    all_red = InlineKeyboardButton(f'Все на красное 🔴',
                                                   callback_data=f'ruletke_all_красное_{message.chat.id}_{message.from_user.id}')
                    # все На черное
                    all_black = InlineKeyboardButton(f'Все на черное ⚫️',
                                                     callback_data=f'ruletke_all_черное_{message.chat.id}_{message.from_user.id}')
                    # все На зеленое
                    all_green = InlineKeyboardButton(f'Все на зеленое 🟢',
                                                     callback_data=f'ruletke_all_зеленое_{message.chat.id}_{message.from_user.id}')
                    key.add(all_red, all_black, all_green)

                    spin = InlineKeyboardButton(f'Крутить рулетку',
                                                callback_data=f'ruletke_spin_{message.chat.id}_{message.from_user.id}')
                    update = InlineKeyboardButton(f'Обновить ставки',
                                                  callback_data=f'ruletke_update_{message.chat.id}_{message.from_user.id}')
                    key.add(spin, update)

                    leave = InlineKeyboardButton(f'Уйти из игры',
                                                 callback_data=f'ruletke_leave_{message.chat.id}_{message.from_user.id}')
                    key.add(leave)
                    # список игроков
                    gamers = []
                    with open(f'{path}/game/casino/games/{message.chat.id}_{message.from_user.id}.json', 'r', encoding='utf-8') as f:
                        game_data = json.load(f)
                        f.close()
                        for gamer in game_data['игроки']:
                            user_info = database.users.find_one({'id': gamer})
                            gamers.append(f'{await username_2(gamer, user_info["username"])} ')
                        msg_data = []
                        msg_data.append(
                            f'{await username(message)}, начал игру за {num} столиком!\n'
                            f'Внимание игроки: {"".join(gamers)}\n'
                            f'Делайте ставки, ставка стола: {game_data["ставка"]}$\n')
                        stavki = game_data['ставки']
                        chetn = ['2', '4', '6', '8', '10', '12', '14', '16', '18', '20', '22', '24']
                        ne_chetn = ['1', '3', '5', '7', '9', '11', '13', '15', '17', '19', '21',
                                    '23']
                        for user in range(0, len(stavki)):
                            us_info = database.users.find_one({'id': list(stavki[user])[0]})
                            for num in list(stavki[user][list(stavki[user])[0]]):
                                if num in chetn:
                                    msg_data.append(
                                        f'{await username_2(us_info["id"], us_info["username"])} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num}🔴\n')
                                elif num in ne_chetn:
                                    msg_data.append(
                                        f'{await username_2(us_info["id"], us_info["username"])} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num}⚫️\n')
                                elif num == '0':
                                    msg_data.append(
                                        f'{await username_2(us_info["id"], us_info["username"])} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num}🟢\n')
                                elif num == 'красное':
                                    msg_data.append(
                                        f'{await username_2(us_info["id"], us_info["username"])} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num} 🔴\n')
                                elif num == 'черное':
                                    msg_data.append(
                                        f'{await username_2(us_info["id"], us_info["username"])} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num} ⚫️\n')
                                elif num == 'зеленое':
                                    msg_data.append(
                                        f'{await username_2(us_info["id"], us_info["username"])} сделал ставку {stavki[user][list(stavki[user])[0]][num]}$ на {num} 🟢\n')
                        await bot.send_message(message.chat.id,''.join(msg_data),
                                                    reply_markup=key,
                                               parse_mode='Markdown')
                        await asyncio.sleep(60*30)
                        while True:
                            with open(f'{path}/game/casino/games/{message.chat.id}_{message.from_user.id}.json', 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                f.close()
                                if not data['запущ_рулетка']:
                                    # игра больше не существет
                                    os.remove(f'{path}/game/casino/games/{message.chat.id}_{message.from_user.id}.json')
                                    # вернуть ставки обратно если будут
                                    arr = next(os.walk(f'{os.getcwd()}/game/casino/games'))[2]
                                    if f'{message.chat.id}_{message.from_user.id}.json' in arr:
                                        with open(
                                                f'{os.getcwd()}/game/casino/games/{message.chat.id}_{message.from_user.id}.json',
                                                'r', encoding='utf-8') as f:
                                            data = json.load(f)
                                            f.close()
                                            stavki = data['ставки']

                                            for user in stavki:
                                                user_id = list(user.keys())[0]
                                                us_info = database.users.find_one({'id': user_id})
                                                stavki_user = user[user_id]
                                                for stavka in list(stavki_user.keys()):
                                                    database.users.update_one({'id': user_id},
                                                                              {'$set': us_info['cash'] + stavki_user[
                                                                                  stavka]})
                                    await bot.send_message(message.chat.id, 'Игра была звершена, ставки вернуты владельцам!\n'
                                                                            'Чтобы создать новую, напишите Создать игру!')
                                    break
                                else:
                                    await asyncio.sleep(5)
    else:
        arr = next(os.walk(f'{path}/game/casino/games'))[2]
        key = InlineKeyboardMarkup()
        num = 1
        for i in arr:
            if str(message.chat.id) in i:
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
        await bot.send_message(message.chat.id, f'Выберите столик:', reply_markup=key)
def register_handlers_krupye(dp: Dispatcher):
    dp.register_message_handler(create_game, content_types='text', text=['создать игру', 'Создать игру'])
    dp.register_message_handler(stavka, commands='stavka')
    dp.register_message_handler(rulette,content_types='text', text=['Рулетка', 'рулетка'])