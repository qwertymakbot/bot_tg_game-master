import os

from bot import check_user, database, types, username_2, parser, bot, Dispatcher, res_database, add_time_min, scheduler, \
    InlineKeyboardMarkup, InlineKeyboardButton
import json
import pytz
import datetime
import asyncio
from bot import username
from create_bot import dp


# /mybus Мой бизнес
async def mybus(message: types.Message):
    # президент купил страну сразу гражданин
    await check_user(message)
    bus_data = database.users_bus.find_one({'boss': message.from_user.id})
    if bus_data is None:
        await message.answer(f'{await username(message)}, у вас нет бизнеса!', parse_mode='HTML')
    else:
        work_people = list(database.autocreater_work.find({'boss': message.from_user.id}))
        await message.answer(f'{await username(message)}, ваш бизнес:\n'
                             f'™️ Название: {bus_data["name"]}\n'
                             f'🛠 Что производит: {bus_data["product"]}\n'
                             f'👨‍🏫 Автосборщиков: {len(work_people)} из {bus_data["work_place"]} чел.\n'
                             f'🕐 Время производства 1 единицы продукции: {bus_data["time_to_create"]} минут\n\n'
                             f'❗️ Для продажи бизнеса введите /sell_bus', parse_mode='HTML')


# /sell_bus Продать бизнес
async def sell_bus(message: types.Message):
    await check_user(message)
    user_info = database.users.find_one({'id': message.from_user.id})
    if user_info['job'] == 'Предприниматель':
        # проверка есть ли бизнес уже
        bus_info = database.users_bus.find_one({'boss': message.from_user.id})
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
            await bot.send_message(message.chat.id,
                                   f'{await username(message)}, для начала вам нужно установить плату строителям за работу!\n'
                                   f'Установить плату можно только 1 раз!', parse_mode='HTML')
            return
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
                                  args=(message.from_user.id,), id=f'{message.from_user.id}_build', timezone=tz)
                await bot.send_message(message.chat.id,
                                       f'{await username(message)}, начал строительство объекта {users_bus["name"]} {users_bus["product"]}\n'
                                       f'❗️ Стройка закончится через 24 часа ❗️', parse_mode='HTML')
            else:
                await bot.send_message(message.chat.id,
                                       f'{await username(message)}, у вас недостаточно строителей, нужно ещё {users_bus["need_builder"] - len(builders)}',
                                       parse_mode='HTML')
            return
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
                                   f'{await username(message)}, вы уже строите, вам ещё осталось {result}',
                                   parse_mode='HTML')
        else:
            await bot.send_message(message.chat.id, f'{await username(message)}, вы уже построили свой бизнес!',
                                   parse_mode='HTML')
    else:
        await bot.send_message(message.chat.id,
                               f'{await username_2(message.from_user.id, message.from_user.first_name)}, данная команда доступна только Предпринимателю',
                               parse_mode='HTML')


# /cancel_bus Отмена строительства
async def cancel_bus(message: types.Message):
    await check_user(message)
    user_info = database.users.find_one({'id': message.from_user.id})
    if user_info['job'] == 'Предприниматель':
        bus_info = database.users_bus.find_one({'boss': message.from_user.id})
        if bus_info['status'] == 'building':
            key = InlineKeyboardMarkup()
            but_yes = InlineKeyboardButton('Да ✅', callback_data=f'cancel_bus_yes_{str(message.from_user.id)[-3::]}')
            but_no = InlineKeyboardButton('Нет ❌', callback_data=f'cancel_bus_no_{str(message.from_user.id)[-3::]}')
            key.add(but_yes, but_no)
            await bot.send_message(message.chat.id,
                                   f'{await username(message)}, вы действительно хотите отменить строительство вашего бизнеса?\n'
                                   f'{bus_info["name"]} {bus_info["product"]}\n'
                                   f'❗️ Все ресурсы будут возвращены на 50%, также выдана зарплата '
                                   f'строителям на 50%', reply_markup=key, parse_mode='HTML')
        else:
            await bot.send_message(message.chat.id, f'{await username(message)}, ваш бизнес не строится!',
                                   parse_mode='HTML')
    else:
        await bot.send_message(message.chat.id,
                               f'{await username(message)}, данная команда доступна только Предпринимателю',
                               parse_mode='HTML')


# /bpay Установление платы каждому строителю
async def bpay(message: types.Message):
    await check_user(message)
    try:
        pay = int(message.get_args().split()[0])
        print(pay)
        user_info = database.users.find_one({'id': message.from_user.id})
        if user_info['job'] == 'Предприниматель':
            bus_info = database.users_bus.find_one({'boss': message.from_user.id})
            if bus_info['bpay'] == 0:
                if user_info['cash'] >= pay * bus_info['need_builder']:
                    database.users.update_one({'id': message.from_user.id},
                                              {'$set': {'cash': user_info['cash'] - pay * bus_info['need_builder']}})
                    database.users_bus.update_one({'boss': message.from_user.id}, {'$set': {'bpay': pay,
                                                                                            'status': 'need_builders'}})
                    await bot.send_message(message.chat.id,
                                           f'{await username(message)}, вы успешно установили плату строителям за работу в размере {pay} $',
                                           parse_mode='HTML')
            else:
                await bot.send_message(message.chat.id,
                                       f'{await username(message)}, плату за строительство можно установить только 1 раз',
                                       parse_mode='HTML')
        else:
            await bot.send_message(message.chat.id,
                                   f'{await username(message)}, данная команда доступна только Предпринимателю',
                                   parse_mode='HTML')
    except:
        await bot.send_message(message.chat.id, f'{await username(message)}, вы некорректно ввели плату (/bpay 100)',
                               parse_mode='HTML')


# /buybus Покупка бизнеса
async def buybus(message: types.Message):
    await check_user(message)
    user_info = database.users.find_one({'id': message.from_user.id})
    if database.users_bus.find_one({'boss': message.from_user.id}) is not None:
        await bot.send_message(message.chat.id, f'{await username(message)}, у вас уже есть бизнес!', parse_mode='HTML')
        return
    if user_info['citizen_country'] != 'нет':
        key = InlineKeyboardMarkup()
        but_auto = InlineKeyboardButton('Автомобиль', callback_data=f'Биз_Авто')
        but_crypto = InlineKeyboardButton('Крипта', callback_data=f'Биз_Крипта')
        key.add(but_auto, but_crypto)
        await bot.send_message(message.chat.id, 'Выберите бизнес:', reply_markup=key)
    else:
        await bot.send_message(message.chat.id,
                               f'{await username(message)}, для начала вам нужно стать гражданином страны!',
                               parse_mode='HTML')


@dp.callback_query_handler(lambda callback: 'Биз_Авто' == callback.data)
async def bus_auto(callback: types.CallbackQuery):
    key = InlineKeyboardMarkup(row_width=3)
    but_nazad = InlineKeyboardButton('◀️', callback_data=f'buybus_naz_{str(callback.from_user.id)[-3::]}_0')
    but_vpered = InlineKeyboardButton('▶️', callback_data=f'buybus_vper_{str(callback.from_user.id)[-3::]}_0')
    but_buy = InlineKeyboardButton('Купить 💲', callback_data=f'buybus_buy_{str(callback.from_user.id)[-3::]}_0')
    but_otmena = InlineKeyboardButton('Отмена ❌', callback_data=f'buybus_otm_{str(callback.from_user.id)[-3::]}')
    key.add(but_nazad, but_buy, but_vpered, but_otmena)
    user_info = database.users.find_one({'id': callback.from_user.id})
    bus_data = list(database.businesses.find({'country': user_info['citizen_country']}))
    if not bus_data:
        await bot.send_message(callback.message.chat.id, 'в вашей стране нет бизнеса')
    await bot.send_message(callback.message.chat.id, f'Страна производства: {bus_data[0]["country"]}\n'
                                                     f'Что производит: {bus_data[0]["product"]}\n'
                                                     f'🖤 Топлива: {bus_data[0]["oil"]} л\n'
                                                     f'🍔 Еда: {bus_data[0]["food"]} кг\n'
                                                     f'💵 Цена: {bus_data[0]["cost"]} $\n\n'
                                                     f'Страница 1/{len(bus_data)}', reply_markup=key)


@dp.callback_query_handler(lambda callback: 'Биз_Крипта' == callback.data)
async def bus_crypto(callback: types.CallbackQuery):
    await callback.message.edit_text('Soon...')


async def end_build_bus(user_id):
    boss_info = database.users.find_one({'id': user_id})
    builders_info = list(database.builders_work.find({'boss': user_id}))
    bus_info = database.users_bus.find_one({'boss': user_id})
    # Изменение статуса стройки
    database.users_bus.update_one({'boss': user_id}, {'$set': {'status': 'work'}})
    # Выдача денег строителям\расформирование их
    for builder in builders_info:
        builder_info = database.users.find_one({'id': builder['builder']})
        job_info = database.jobs.find_one({'name_job': builder_info['job']})
        database.users.update_one({'id': builders_info['builder']},
                                  {'$set': {'cash': builder_info['cash'] + bus_info['bpay'],
                                            'exp': builder_info['exp'] + job_info['exp_for_job']}})
        database.builders_work.delete_one({'builder': builder['builder']})

        await bot.send_message(builder['builder'],
                               f'{await username_2(builder_info["id"], builders_info["firstname"])}, вы получили вознаграждение за стройку объекта {bus_info["name"]} {bus_info["product"]}\n'
                               f'💵 +{bus_info["bpay"]}\n'
                               f'🏵 +{job_info["exp_for_job"]}', parse_mode='HTML')
    res_database.build_bus.delete_one({'boss': user_id})

    await bot.send_message(user_id,
                           f'{await username_2(user_id, boss_info["firstname"])}, ваш бизнес {bus_info["name"]} {bus_info["product"]} завершил стройку!',
                           parse_mode='HTML')


def register_handlers_predprinimatel(dp: Dispatcher):
    dp.register_message_handler(mybus, commands='mybus')
    dp.register_message_handler(sell_bus, commands='sell_bus')
    dp.register_message_handler(cancel_bus, commands='cancel_bus')
    dp.register_message_handler(build_bus, commands='build_bus')
    dp.register_message_handler(bpay, commands='bpay')
    dp.register_message_handler(buybus, commands='buybus')
