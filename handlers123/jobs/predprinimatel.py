import os

from bot import check_user, database, types, username_2, parser, bot, Dispatcher
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
        await message.answer(f'{await username(message)}, у вас нет бизнеса!', parse_mode='Markdown')
    else:
        with open(f'./game/bus_workplace/{message.from_user.id}.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            work_people = data['users_id']
        await message.answer(f'{await username(message)}, ваш бизнес:\n'
                             f'™️ Название: {bus_data["name"]}\n'
                             f'🛠 Что производит: {bus_data["product"]}\n'
                             f'👨‍🏫 Автосборщиков: {len(work_people)} из {bus_data["work_place"]} чел.\n'
                             f'🕐 Время производства 1 единицы продукции: {bus_data["time_to_create"]} минут\n\n'
                             f'❗️ Для продажи бизнеса введите /sell_bus', parse_mode='Markdown')


# /sell_bus Продать бизнес
async def sell_bus(message: types.Message):
    await check_user(message)
    user_info = database.users.find_one({'id': message.from_user.id})
    if user_info['job'] == 'Предприниматель':
        # проверка есть ли бизнес уже
        bus_info = database.users_bus.find_one({'id': message.from_user.id})
        if bus_info is not None:
            key = types.InlineKeyboardMarkup()
            but_yes = types.InlineKeyboardButton(text='Продать', callback_data='Бизнес_продать')
            but_no = types.InlineKeyboardButton(text='Не продавать', callback_data='Бизнес_не_продать')
            key.add(but_no, but_yes)
            await message.answer(
                f'{await username(message)}, вы действительно хотите продать бизнес за {int(int(bus_info["cost"]) - int(bus_info["cost"]) * 0.1)}$',
                reply_markup=key, parse_mode='Markdown')
            # запись джсон для продажи цена
            data = {}
            data['cost'] = int(int(bus_info["cost"]) - int(bus_info["cost"]) * 0.1)
            with open(f'{os.getcwd()}/game/sell_bus/{message.from_user.id}.json', 'w', encoding='utf-8') as f:
                json.dump(data, f)
        else:
            await message.answer(f'{await username(message)}, у вас нет бизнеса!', parse_mode='Markdown')




# /build_bus Строить бизнес
async def build_bus(message: types.Message):
    await check_user(message)
    user_info = database.users.find_one({'id': message.from_user.id})
    if user_info['job'] == 'Предприниматель':
        try:
            with open(f'{os.getcwd()}/game/build_bus/{message.from_user.id}.json', 'r', encoding='utf-8') as f:
                build_data = json.load(f)
                isbuilding = build_data['isbuilding']
                f.close()
                if not isbuilding:
                    builders = build_data['builders']
                    if len(builders) == build_data['need_builder'] and not build_data['isbuilding']:
                        name = build_data['name']
                        product = build_data['product']
                        # Текущее время
                        tz = pytz.timezone('Etc/GMT-3')
                        now_time = tz.localize(datetime.datetime.now())
                        build_data['start_time'] = str(now_time)
                        build_data['isbuilding'] = True
                        cash = build_data['builder_pay']
                        with open(f'{os.getcwd()}/game/build_bus/{message.from_user.id}.json', 'w',
                                  encoding='utf-8') as f:
                            json.dump(build_data, f)

                        data = [f"{await username_2(message.from_user.id,message.from_user.username)} начал строительство объекта:\n"
                                f"🏢 {name} {product}\n👷‍♂️ Строители:\n"]
                        for user_id in builders:
                            us_info = database.users.find_one({'id': user_id})
                            data.append(f'{await username_2(us_info["id"], us_info["username"])},')
                        data.append(
                            f'\n\n❗️ Строительство объекта длиться 24 часа, после него все строители получат {cash}$')
                        await message.answer(''.join(data))
                        await asyncio.sleep(120)
                        data.clear()

                        data.append(f'@{message.from_user.username}, стротельство объекта завершено! 🧱\n'
                                    f'Строителям выдана заработная плата +{cash}$ 💰\n')
                        for user_id in builders:
                            builder_info = database.users.find_one({'id': user_id})
                            boss_info = database.users.find_one({'id': message.from_user.id})
                            database.users.update_one({'id': user_id}, {'$set': {'cash': builder_info['cash'] + cash}})
                            database.users.update_one({'id': message.from_user.id},
                                                      {'$set': {'cash': boss_info['cash'] - cash}})
                            database.builders_work.delete_one({'builder': user_id})

                            data.append(f'{await username_2(builder_info["id"], builder_info["username"])},')
                        data.append(f'\n❗️ Для просмотра вышего бизнеса введите /mybus')
                        # добавление бизнеса пользователя в БД
                        database.users_bus.insert_one({'id': message.from_user.id,
                                                       'name': build_data['name'],
                                                       'prouct': build_data['product'],
                                                       'work_place': build_data['work_place'],
                                                       'time_to_create': build_data['time_to_create'],
                                                       'country': build_data['country']})
                        # создание json с указанием работников на предприятии
                        with open(f'./game/bus_workplace/{message.from_user.id}.json', 'w', encoding='utf-8') as f:
                            data = {'users_id': [],
                                    'time_to_create': build_data['time_to_create']}
                            json.dump(data, f)

                        # удаление json build_bus
                        path = os.getcwd()
                        os.remove(path + f'\\game\\build_bus\\{message.from_user.id}.json')
                        await message.answer(''.join(data), parse_mode='Markdown')
                    else:
                        await message.answer(
                            f'{await username_2(message.from_user.id, message.from_user.username)}, вам нужно еще {build_data["need_builder"] - len(builders)} строителей', parse_mode='Markdown')
                else:
                    # Текущее время
                    tz = pytz.timezone('Etc/GMT-3')
                    now_time = tz.localize(datetime.datetime.now())

                    start_time = build_data['start_time']
                    start_time = parser.parse(str(start_time))

                    timeleft = now_time - start_time
                    timeleft = str(timeleft).split('.')
                    timeleft = str(timeleft[0]).split(':')
                    try:
                        int(timeleft[0])
                        hour24 = datetime.timedelta(hours=24, minutes=0, seconds=0)
                        timeleft = datetime.timedelta(hours=int(timeleft[0]), minutes=int(timeleft[1]),
                                                      seconds=int(timeleft[2]))
                        timeleft = hour24 - timeleft
                        await message.answer(
                            f'{await username_2(message.from_user.id, message.from_user.username)}, до окончания стройки вашего бизнеса осталось {timeleft}', parse_mode='Markdown')
                    except:
                        cash = build_data['builder_pay']
                        builders = build_data['builders']
                        data = [
                            f'{username_2(message.from_user.id, message.from_user.username)}, стротельство объекта завершено!\n'
                            f'Строителям выдана заработная плата +{cash}$\n']
                        for user_id in builders:
                            builder_info = database.users.find_one({'id': user_id})
                            boss_info = database.users.find_one({'id': message.from_user.id})
                            database.users.update_one({'id': user_id}, {'$set': {'cash': builder_info['cash'] + cash}})
                            database.users.update_one({'id': message.from_user.id},
                                                      {'$set': {'cash': boss_info['cash'] - cash}})
                            database.builders_work.delete_one({'builder': user_id})

                            data.append(f'{await username_2(builder_info["id"], builder_info["username"])},')

                        data.append(f'\n❗️ Для просмотра вышего бизнеса введите /mybus')
                        # добавление бизнеса пользователя в БД
                        database.users_bus.insert_one({'id': message.from_user.id,
                                                       'name': build_data['name'],
                                                       'prouct': build_data['product'],
                                                       'work_place': build_data['work_place'],
                                                       'time_to_create': build_data['time_to_create'],
                                                       'country': build_data['country']})

                        # создание json с указанием работников на предприятии
                        with open(f'{os.getcwd()}/game/bus_workplace/{message.from_user.id}.json', 'w', encoding='utf-8') as f:
                            data_dict = {}
                            data_dict['users_id'] = []
                            json.dump(data_dict, f)
                        # удаление json build_bus
                        path = os.getcwd()
                        os.remove(path + f'\\game\\build_bus\\{message.from_user.id}.json')

                        await message.answer(''.join(data), parse_mode='Markdown')
        except:
            path = os.getcwd()
            os.remove(path + f'\\game\\build_bus\\{message.from_user.id}.json')
            await message.answer(f'{await username_2(message.from_user.id, message.from_user.username)}, у вас нет строек', parse_mode='Markdown')
    else:
        await message.answer(f'{await username_2(message.from_user.id, message.from_user.username)}, данная команда доступна только Предпринимателю', parse_mode='Markdown')


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
                    await message.answer(f'{await username(message)}, во время стройки нельзя отменить её!', parse_mode='Markdown')
        except:
            await message.answer(f'{await username(message)}, в данный момент нет строек!', parse_mode='Markdown')
    else:
        await message.answer(f'{await username(message)}, данная команда доступна только Предпринимателю', parse_mode='Markdown')


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
                            await message.answer(f'{await username(message)}, у вас недостаточно средств!', parse_mode='Markdown')
                            return
                        if build_data['builder_pay'] == 0:
                            with open(f'./game/build_bus/{i}', 'w', encoding='utf-8') as f:
                                build_data['builder_pay'] = pay
                                json.dump(build_data, f)
                                await message.answer(
                                    f'{await username(message)}, каждый строитель по окончанию строительства получит {pay}$\n'
                                    f'❗️Теперь вам нужно найти строителей чтобы начать стройку (команда для строителей - /build)\n'
                                    f'❗️Как только наберется {build_data["need_builder"]} строителей, напишите /build_bus', parse_mode='Markdown')
                                # оповещение босса о том что строители есть, создание команды для начала стройки
                        else:
                            await message.answer(
                                f'{await username(message)}, цену можно устанавливать только один раз', parse_mode='Markdown')
                    except:
                        await message.answer(f'{await username(message)}, пример ввода: /bpay 100', parse_mode='Markdown')


# /buybus Покупка бизнеса
async def buybus(message: types.Message):
    await check_user(message)
    num_business = message.get_args().split()
    user_info = database.users.find_one({'id': message.from_user.id})
    if user_info["citizen_country"] != 'нет':  # Если гражданин страны
        if len(num_business) == 0:  # Если аргументов нет
            bus_data = list(database.businesses.find({'country': user_info['citizen_country']}))
            bus_list = [f'💎 В вашей стране доступны следующие бизнесы:\n']
            for i in range(0, len(bus_data)):
                bus_list.append(f'{i + 1}. {bus_data[i]["name"]} ({bus_data[i]["product"]})\n')
            bus_list.append(
                f'\n❗️ Чтобы купить бизнес введите /buybus 1 (где 1 - позиция бизнеса в текущем списке)')
            await message.answer(''.join(bus_list))
        elif len(num_business) == 1:
            # проверка есть ли бизнес уже
            user_bus = database.users_bus.find_one({'id': message.from_user.id})
            if user_bus is not None:
                await message.answer(f'{await username(message)}, вы уже обладаете бизнесом!\n'
                                     f'💎 {user_bus["name"]} {user_bus["product"]} 💎\n'
                                     f'❗️ Для продажи бизнеса введите /sell_bus', parse_mode='Markdown')
                return
            try:
                num_business = int(num_business[0])
                bus_data = list(database.businesses.find({'country': user_info['citizen_country']}))
                if user_info['job'] == 'Предприниматель':
                    if user_info['oil'] >= bus_data[num_business - 1]['oil']:
                        if user_info['food'] >= bus_data[num_business - 1]['food']:
                            if user_info['cash'] >= bus_data[num_business - 1]['cost']:
                                try:
                                    with open(f'{os.getcwd()}/game/build_bus/{message.from_user.id}.json', 'r',
                                              encoding='utf-8') as f:
                                        build_data = json.load(f)
                                        isbuilding = 'строится' if build_data['isbuilding'] == True else 'ожидание'
                                        await message.answer(
                                            f'{await username(message)}, у вас незаконченная стройка 🧱\n'
                                            f'™️ Название: {build_data["name"]}\n'
                                            f'🛠 Что производит: {build_data["product"]}\n'
                                            f'👷‍♂️ Количество строителей: {len(build_data["builders"])} из {build_data["need_builder"]}\n'
                                            f'⚙️ Состояние стройки: {isbuilding}', parse_mode='Markdown')

                                except:
                                    with open(f'{os.getcwd()}/game/build_bus/{message.from_user.id}.json', 'w',
                                              encoding='utf-8') as f:
                                        build_data = {}
                                        build_data['country'] = bus_data[num_business - 1]['country']
                                        build_data['name'] = bus_data[num_business - 1]['name']
                                        build_data['product'] = bus_data[num_business - 1]['product']
                                        build_data['need_builder'] = bus_data[num_business - 1]['need_builder']
                                        build_data['oil'] = bus_data[num_business - 1]['oil']
                                        build_data['food'] = bus_data[num_business - 1]['food']
                                        build_data['cost'] = bus_data[num_business - 1]['cost']
                                        build_data['work_place'] = bus_data[num_business - 1]['work_place']
                                        build_data['time_to_create'] = bus_data[num_business - 1]['time_to_create']
                                        build_data['builders'] = []
                                        build_data['builder_pay'] = 0
                                        build_data['isbuilding'] = False
                                        json.dump(build_data, f)
                                        # Снятие с баланса пользователя ресурсов
                                        database.users.update_one({'id': message.from_user.id}, {'$set': {'oil': user_info['oil'] - bus_data[num_business - 1]['oil'],
                                                                                                          'food': user_info['food'] - bus_data[num_business - 1]['food'],
                                                                                                          'cash': user_info['cash'] - bus_data[num_business - 1]['cost']}})
                                        # Добавление ресурсов на счет государства
                                        country_info = database.countries.find_one({'country': user_info['citizen_country']})
                                        database.countries.update_one({'country': user_info['country_citizen']}, {'$set': {'oil': country_info['oil'] + bus_data[num_business - 1]['oil'],
                                                                                                          'food': country_info['food'] + bus_data[num_business - 1]['food'],
                                                                                                          'cash': country_info['cash'] + bus_data[num_business - 1]['cost']}})
                                        # оповещение о снятие денег и о создании заявки
                                        await message.answer(
                                            f'{await username(message)}, вам был веделен участок для строительства, а также сняты с баланса все необходимые ресурсы ⚙️\n\n'
                                            f'❗️ Вам необходимо установить плату за работу каждому строителю (/bpay 10 - где 10 цена в $ каждому строителю за выполненную работу)\n', parse_mode='Markdown')

                            else:
                                await message.answer(f'{await username(message)}, у вас недостаточно денег $', parse_mode='Markdown')
                        else:
                            await message.answer(f'{await username(message)}, у вас недостаточно еды 🍔', parse_mode='Markdown')
                    else:
                        await message.answer(f'{await username(message)}, у вас недостаточно нефти 🖤', parse_mode='Markdown')
                else:
                    await message.answer(f'{await username(message)}, вы должны работать Предпринимателем', parse_mode='Markdown')

            except:
                print('predprinimatel 340')
    else:
        await message.answer(
            f'{await username(message)}, вы должны являться гражданином одной из стран! (/citizen)')


# /bus Все бизнесы
async def bus(message):
    await check_user(message)
    num_business = message.get_args().split()
    if len(num_business) == 0:
        business_data = list(database.businesses.find())
        cars_list = ['💎 Бизнесы в мире:\n']
        for i in range(0, len(business_data)):
            cars_list.append(f'{i + 1}. {business_data[i]["country"]} {business_data[i]["name"]} ({business_data[i]["product"]})\n')
        cars_list.append(
            f'\n❗️ Чтобы узнать подробнее о бизнесе введите /bus 1 (где 1 - позиция бизнеса в текущем списке)\n'
            f'💰 Чтобы купить бизнес введите /buybus')
        await message.answer(''.join(cars_list))
    elif len(num_business) == 1:
        try:
            num_business = int(num_business[0])
            business_data = list(database.businesses.find())
            await message.answer(f'💎 О бизнесе:\n'
                                 f'🌐 Страна: {business_data[num_business - 1]["country"]}\n'
                                 f'™️ Название: {business_data[num_business - 1]["name"]}\n'
                                 f'🛠 Что производит: {business_data[num_business - 1]["product"]}\n'
                                 f'👷‍♂️ Нужно строителей для стройки: {business_data[num_business - 1]["need_builder"]}\n'
                                 f'🖤 Нужно нефти: {business_data[num_business - 1]["oil"]}л\n'
                                 f'🍔 Нужно еды: {business_data[num_business - 1]["food"]}кг\n'
                                 f'💰 Стоимость производства: {business_data[num_business - 1]["cost"]}$\n'
                                 f'👨‍👨‍👦️ Рабочих мест: {business_data[num_business - 1]["work_place"]}\n'
                                 f'🕐 Время производства 1 ед. продукции: {business_data[num_business - 1]["time_to_create"]}мин')
        except:
            print('predprinimatel 374')


def register_handlers_predprinimatel(dp: Dispatcher):
    dp.register_message_handler(mybus, commands='mybus')
    dp.register_message_handler(sell_bus, commands='sell_bus')
    dp.register_message_handler(cancel_bus, commands='cancel_bus')
    dp.register_message_handler(build_bus, commands='build_bus')
    dp.register_message_handler(bpay, commands='bpay')
    dp.register_message_handler(buybus, commands='buybus')
    dp.register_message_handler(bus, commands='bus')
