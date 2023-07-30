import os

from bot import *


# /leave_creater Уйти с автосборки
async def leave_creater(message):
    await check_user(message)
    with sqlite3.connect('game/data.db', timeout=10) as conn:
        cur = conn.cursor()
        isWorking = cur.execute("""SELECT working FROM users WHERE user_id = ?""", (message.from_user.id,)).fetchone()
        if not isWorking[0]:  # Если не работает
            boss = cur.execute("""SELECT boss FROM autocreater_work WHERE creater = ?""",
                               (message.from_user.id,)).fetchone()
            if boss is not None:  # Если устроен на предприятие
                # Удаление из таблицы
                cur.execute("""DELETE FROM autocreater_work WHERE creater = ?""", (message.from_user.id,))
                conn.commit()
                # Удаление из bus_workplace
                path = os.getcwd()
                with open(f'{path}/game/bus_workplace/{boss[0]}.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    f.close()
                    with open(f'{path}/game/bus_workplace/{boss[0]}.json', 'w', encoding='utf-8') as f:
                        data['users_id'].remove(message.from_user.id)
                        json.dump(data, f)
                        f.close()
                await message.answer(f'@{message.from_user.username}, вы успешно уволились с предприятия!')
            else:
                await message.answer(f'@{message.from_user.username}, вы не устроены на предприятие!')

        else:  # Если работает
            await message.answer(f'@{message.from_user.username}, для начала окончите работу!')
        cur.close()


# /creater Автосборщик
async def creater(message):
    await check_user(message)
    with sqlite3.connect('game/data.db', timeout=10) as conn:
        cur = conn.cursor()
        num_bus = message.get_args().split()
        job = cur.execute("""SELECT job FROM users WHERE user_id = ?""", (message.from_user.id,)).fetchone()
        country = cur.execute("""SELECT citizen_country FROM users WHERE user_id = ?""",
                              (message.from_user.id,)).fetchone()
        if job[0] != 'Автосборщик':
            await message.answer(f'@{message.from_user.username}, данная команда доступна только Автосборщикам!')
            return

        if len(num_bus) == 0:
            bus_data = cur.execute(
                """SELECT user_id, name, product, work_place FROM users_bus WHERE country = ?""", (country[0],)).fetchall()
            bus_list = []
            bus_list.append('🚗 Список предприятий:\n')
            for i in range(0, len(bus_data)):
                with open(f'{os.getcwd()}/game/bus_workplace/{bus_data[i][0]}.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if len(data['users_id']) < bus_data[i][3]:
                        bus_list.append(f'{i + 1}. {bus_data[i][1]} {bus_data[i][2]}\n')
            bus_list.append(
                f'\n❗️ Чтобы устроиться введите /creater 1 (где 1 - позиция предприятия в текущем списке)')
            await message.answer(''.join(bus_list))
        elif len(num_bus) == 1:
            try:
                num_bus = int(num_bus[0])

                bus_data = cur.execute(
                    """SELECT user_id, name, product, work_place, time_to_create FROM users_bus WHERE country = ?""",
                    (country[0],)).fetchall()
                with open(f'{os.getcwd()}/game/bus_workplace/{bus_data[num_bus - 1][0]}.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    users_id_list = data['users_id']
                    users_id_list.append(message.from_user.id)
                    data['users_id'] = users_id_list
                    data['time_to_create'] = bus_data[num_bus - 1][4]
                    f.close()
                    path = os.getcwd()
                    with open(f'{path}/game/bus_workplace/{bus_data[num_bus - 1][0]}.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f)
                    cur.execute("""INSERT INTO autocreater_work VALUES(?,?)""",
                                (message.from_user.id, bus_data[num_bus - 1][0]))
                    conn.commit()

                await message.answer(f'@{message.from_user.username}, вы успешно устроились на предприятие!')

            except:
                print('ошибка')
        cur.close()


# Регистрация хендлеров
def register_handlers_autocreater(dp: Dispatcher):
    dp.register_message_handler(leave_creater, commands='leave_creater')
    dp.register_message_handler(creater, commands='creater')
