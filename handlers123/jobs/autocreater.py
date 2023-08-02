import os

from bot import *


# /leave_creater Уйти с автосборки
async def leave_creater(message: types.Message):
    await check_user(message)
    res_job = res_database.job.find_one({'id': message.from_user.id})

    if not res_job['working']:  # Если не работает
        autocreater_info = database.autocreater_work.find_one({'creater': message.from_user.id})

        if autocreater_info is not None:  # Если устроен на предприятие
            # Удаление из док-та
            database.autocreater_work.delete_one({'creater': message.from_user.id})
            # Удаление из bus_workplace
            database.bus_workplace.delete_one({'creater': message.from_user.id})
            await bot.send_message(message.chat.id, f'{await username(message)}, вы успешно уволились с предприятия!', parse_mode='HTML')
        else:
            await bot.send_message(message.chat.id, f'{await username(message)}, вы не устроены на предприятие!', parse_mode='HTML')

    else:  # Если работает
        await bot.send_message(message.chat.id, f'{await username(message)}, для начала окончите работу!', parse_mode='HTML')


# /creater Автосборщик
async def creater(message):
    await check_user(message)
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


# Регистрация хендлеров
def register_handlers_autocreater(dp: Dispatcher):
    dp.register_message_handler(leave_creater, commands='leave_creater')
    dp.register_message_handler(creater, commands='creater')
