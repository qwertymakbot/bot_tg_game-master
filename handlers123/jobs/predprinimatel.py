import os

from bot import check_user, database, types, username_2, parser, bot, Dispatcher, res_database, add_time_min, scheduler, \
    InlineKeyboardMarkup, InlineKeyboardButton
import json
import pytz
import datetime
import asyncio
from bot import username


# /mybus Мой бизнес
async def mybus(message: types.Message):
    # президент купил страну сразу гражданин
    await check_user(message)
    bus_data = database.users_bus.find_one({'id': message.from_user.id})
    if bus_data is None:
        await message.answer(f'{await username(message)}, у вас нет бизнеса!', parse_mode='HTML')
    else:
        work_people = database.autocreater_work.find_one({'boss': message.from_user.id})
        await message.answer(f'{await username(message)}, ваш бизнес:\n'
                             f'™️ Название: {bus_data["name"]}\n'
                             f'🛠 Что производит: {bus_data["product"]}\n'
                             f'👨‍🏫 Автосборщиков: {len(work_people["work_place"])} из {bus_data["work_place"]} чел.\n'
                             f'🕐 Время производства 1 единицы продукции: {bus_data["time_to_create"]} минут\n\n'
                             f'❗️ Для продажи бизнеса введите /sell_bus', parse_mode='HTML')


# /sell_bus Продать бизнес
async def sell_bus(message: types.Message):
    await check_user(message)
    user_info = database.users.find_one({'id': message.from_user.id})
    if user_info['job'] == 'Предприниматель':
        # проверка есть ли бизнес уже
        bus_info = database.users_bus.find_one({'id': message.from_user.id})
        if bus_info is not None:
            key = types.InlineKeyboardMarkup()
            but_yes = types.InlineKeyboardButton(text='Продать',
                                                 callback_data=f'sell_bus_{str(message.from_user.id)[-3::]}_{bus_info["cost"] * 0.5}')
            but_no = types.InlineKeyboardButton(text='Не продавать',
                                                callback_data=f'cancel_bus_{str(message.from_user.id)[-3::]}')
            key.add(but_no, but_yes)
            await message.answer(
                f'{await username(message)}, вы действительно хотите продать бизнес за {bus_info["cost"] * 0.5}$',
                reply_markup=key, parse_mode='HTML')
        else:
            await message.answer(f'{await username(message)}, у вас нет бизнеса!', parse_mode='HTML')


# buy - купил только что
# need_builders - набор строителей
# building - строится
# work - работает
# /build_bus Строить бизнес
async def build_bus(message: types.Message):
    await check_user(message)
    user_info = database.users.find_one({'id': message.from_user.id})
    if user_info['job'] == 'Предприниматель':
        users_bus = database.users_bus.find_one({'boss': message.from_user.id})
        if users_bus is None:
            await bot.send_message(message.chat.id, f'{await username(message)}, для начала нужно приобрести бизнес!',
                                   parse_mode='HTML')
            return
        if users_bus['status'] == 'buy':
            # Изменение статуса бизнеса
            database.users_bus.update_one({'boss': message.from_user.id}, {'$set': {'status': 'need_builders'}})
            # Получение кол-ва строителей на стройке
            builders = list(database.builders_work.find({'boss': message.from_user.id}))
            if len(builders) == users_bus["need_builder"]:
                # Изменение статуса бизнеса
                database.users_bus.update_one({'boss': message.from_user.id}, {'$set': {'status': 'building'}})
                # SCHEDULER
                res_database.build_bus.insert_one({'boss': message.from_user.id,
                                                   'time': await add_time_min(1440)})
                tz = pytz.timezone('Etc/GMT-3')
                scheduler.add_job(end_build_bus, "date",
                                  run_date=await add_time_min(1440),
                                  args=(message.from_user.id,), timezone=tz)
                await bot.send_message(message.chat.id,
                                       f'{await username(message)}, начал строительство объекта {users_bus["name"]} {users_bus["product"]}\n'
                                       f'❗️ Стройка закончится через 24 часа ❗️')
            else:
                await bot.send_message(message.chat.id,
                                       f'{await username(message)}, у вас недостаточно строителей, нужно ещё {users_bus["need_builder"] - len(builders)}')
        if users_bus['status'] == 'need_builders':
            # Получение кол-ва строителей на стройке
            builders = list(database.builders_work.find({'boss': message.from_user.id}))
            if len(builders) == users_bus["need_builder"]:
                # Изменение статуса бизнеса
                database.users_bus.update_one({'boss': message.from_user.id}, {'$set': {'status': 'building'}})
                # SCHEDULER
                res_database.build_bus.insert_one({'boss': message.from_user.id,
                                                   'time': await add_time_min(1440)})
                tz = pytz.timezone('Etc/GMT-3')
                scheduler.add_job(end_build_bus, "date",
                                  run_date=await add_time_min(1440),
                                  args=(message.from_user.id,), timezone=tz)
                await bot.send_message(message.chat.id,
                                       f'{await username(message)}, начал строительство объекта {users_bus["name"]} {users_bus["product"]}\n'
                                       f'❗️ Стройка закончится через 24 часа ❗️')
            else:
                await bot.send_message(message.chat.id,
                                       f'{await username(message)}, у вас недостаточно строителей, нужно ещё {users_bus["need_builder"] - len(builders)}')
        if users_bus["status"] == 'building':
            res_building = res_database.build_bus.find_one({'boss': message.from_user.id})
            # Получение переменных с строки
            tz = pytz.timezone('Etc/GMT-3')
            date, time = res_building['time'].split(' ')
            year, month, day = date.split('-')
            hour, minute, second = time.split(':')
            time_job = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
            time_now = datetime.datetime(datetime.datetime.now(tz=tz).year, datetime.datetime.now(tz=tz).month,
                                         datetime.datetime.now(tz=tz).day, datetime.datetime.now(tz=tz).hour,
                                         datetime.datetime.now(tz=tz).minute, datetime.datetime.now(tz=tz).second)
            result = time_job - time_now
            await bot.send_message(message.chat.id,
                                   f'{await username(message)}, вы уже работаете, вам ещё осталось {result}',
                                   parse_mode='HTML')
        else:
            await bot.send_message(message.chat.id, f'{await username(message)}, вы уже построили свой бизнес!')
    else:
        await bot.send_message(
            f'{await username_2(message.from_user.id, message.from_user.first_name)}, данная команда доступна только Предпринимателю',
            parse_mode='HTML')


# /cancel_bus Отмена строительства
async def cancel_bus(message):
    await check_user(message)
    user_info = database.users.find_one({'id': message.from_user.id})
    if user_info['job'] == 'Предприниматель':
        try:
            path = os.getcwd()
            with open(f'{path}/game/build_bus/{message.from_user.id}.json', 'r', encoding='utf-8') as f:
                build_data = json.load(f)
                isbuilding = build_data['isbuilding']
                f.close()
                if not isbuilding:
                    # Запись данных о бизнесе
                    data = {'oil': build_data['oil'],
                            'food': build_data['food'],
                            'cost': build_data['cost'],
                            'builders': build_data['builders'],
                            'builder_pay': build_data['builder_pay']}
                    path = os.getcwd()
                    with open(f'{path}/game/cancel_bus/{message.from_user.id}.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f)
                        f.close()
                    # Создание кнопок подтверждения
                    key = types.InlineKeyboardMarkup()
                    but_yes = types.InlineKeyboardButton(text='Согласиться', callback_data='Стройка_отмена_да')
                    but_no = types.InlineKeyboardButton(text='Отказаться', callback_data='Стройка_отмена_нет')
                    key.add(but_no, but_yes)
                    await bot.send_message(message.chat.id,
                                           text=f'{await username(message)}, вы действительно хотите прервать стройку?\n'
                                                f'❗️ Вам буду возвращены лишь 50% ресурсов, а также зарплата строителей будет оплачена на 50%',
                                           reply_markup=key, parse_mode='Markdown')
                else:
                    await message.answer(f'{await username(message)}, во время стройки нельзя отменить её!',
                                         parse_mode='Markdown')
        except:
            await message.answer(f'{await username(message)}, в данный момент нет строек!', parse_mode='Markdown')
    else:
        await message.answer(f'{await username(message)}, данная команда доступна только Предпринимателю',
                             parse_mode='Markdown')


# /bpay Установление платы каждому строителю
async def bpay(message: types.Message):
    await check_user(message)
    pay = message.get_args().split()
    arr = next(os.walk(f'{os.getcwd()}/game/build_bus'))[2]
    for i in arr:
        build_data_json = str(i).replace('.json', '')
        if message.from_user.id == int(build_data_json):
            with open(f'{os.getcwd()}/game/build_bus/{i}', 'r', encoding='utf-8') as f:
                build_data = json.load(f)
                isbuilding = build_data['isbuilding']
                if len(pay) == 1 and isbuilding == False:
                    try:
                        user_info = database.users.find_one({'id': message.from_user.id})
                        pay = int(pay[0])
                        if user_info['cash'] < pay * build_data['need_builder']:
                            await message.answer(f'{await username(message)}, у вас недостаточно средств!',
                                                 parse_mode='Markdown')
                            return
                        if build_data['builder_pay'] == 0:
                            with open(f'./game/build_bus/{i}', 'w', encoding='utf-8') as f:
                                build_data['builder_pay'] = pay
                                json.dump(build_data, f)
                                await message.answer(
                                    f'{await username(message)}, каждый строитель по окончанию строительства получит {pay}$\n'
                                    f'❗️Теперь вам нужно найти строителей чтобы начать стройку (команда для строителей - /build)\n'
                                    f'❗️Как только наберется {build_data["need_builder"]} строителей, напишите /build_bus',
                                    parse_mode='Markdown')
                                # оповещение босса о том что строители есть, создание команды для начала стройки
                        else:
                            await message.answer(
                                f'{await username(message)}, цену можно устанавливать только один раз',
                                parse_mode='Markdown')
                    except:
                        await message.answer(f'{await username(message)}, пример ввода: /bpay 100',
                                             parse_mode='Markdown')


# /buybus Покупка бизнеса
async def buybus(message: types.Message):
    await check_user(message)
    user_info = database.users.find_one({'id': message.from_user.id})
    if database.users_bus.find_one({'boss': message.from_user.id}) is not None:
        await bot.send_message(message.chat.id, f'{await username(message)}, у вас уже есть бизнес!')
        return
    if user_info['citizen_country'] != 'нет':
        key = InlineKeyboardMarkup(row_width=3)
        but_nazad = InlineKeyboardButton('◀️', callback_data=f'buybus_naz_{str(message.from_user.id)[-3::]}_0')
        but_vpered = InlineKeyboardButton('▶️', callback_data=f'buybus_vper_{str(message.from_user.id)[-3::]}_0')
        but_buy = InlineKeyboardButton('Купить 💲', callback_data=f'buybus_buy_{str(message.from_user.id)[-3::]}_0')
        but_otmena = InlineKeyboardButton('Отмена ❌', callback_data=f'buybus_otm_{str(message.from_user.id)[-3::]}_0')
        key.add(but_nazad, but_buy, but_vpered, but_otmena)
        bus_data = list(database.businesses.find({'country': user_info['citizen_country']}))
        await bot.send_message(message.chat.id, f'Страна производства: {bus_data[0]["country"]}\n'
                                                f'Что производит: {bus_data[0]["product"]}\n'
                                                f'🖤 Топлива: {bus_data[0]["oil"]} л\n'
                                                f'🍔 Еда: {bus_data[0]["food"]} кг\n'
                                                f'💵 Цена: {bus_data[0]["cost"]} $\n\n'
                                                f'Страница 1/{len(bus_data)}', reply_markup=key)
    else:
        await bot.send_message(message.chat.id,
                               f'{await username(message)}, для начала вам нужно стать гражданином страны!')


async def end_build_bus(user_id):
    user_info = database.users.find_one({'id': user_id})
    builders_info = list(database.builders_work.find({'boss': user_id}))
    bus_info = database.users_bus.find_one({'boss': user_id})
    # Изменение статуса стройки
    database.users_bus.update_one({'boss': user_id}, {'$set': {'status': 'work'}})
    # Выдача денег строителям\расформирование их
    for builder in builders_info:
        ...
    await bot.send_message(user_id,
                           f'{await username_2(user_id, user_info["firstname"])}, ваш бизнес {bus_info["name"]} {bus_info["product"]} завершил стройку!')


def register_handlers_predprinimatel(dp: Dispatcher):
    dp.register_message_handler(mybus, commands='mybus')
    dp.register_message_handler(sell_bus, commands='sell_bus')
    dp.register_message_handler(cancel_bus, commands='cancel_bus')
    dp.register_message_handler(build_bus, commands='build_bus')
    dp.register_message_handler(bpay, commands='bpay')
    dp.register_message_handler(buybus, commands='buybus')
