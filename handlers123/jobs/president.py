from bot import bot, Dispatcher, database, check_user, username, types, InputFile, InlineKeyboardButton, \
    InlineKeyboardMarkup, username_2
import os


# /get_citizen Взять себе гражданина
async def get_citizen(message: types.Message):
    await check_user(message)
    if message.reply_to_message:
        president_info = database.users.find_one({'id': message.from_user.id})
        if president_info['president_country'] != 'нет':  # Если президент страны
            user_info = database.users.find_one({'id': message.reply_to_message.from_user.id})
            if user_info['citizen_country'] == 'нет':  # Если не гражданин
                citizens = database.users.find({'citizen_country': president_info['president_country']})

                country_info = database.countries.find_one({'country': president_info['president_country']})
                if len(list(citizens)) < country_info['max_people']:  # Если гражданинов меньше максимального
                    key = types.InlineKeyboardMarkup()
                    but_yes = types.InlineKeyboardButton(text='Согласиться',
                                                         callback_data=f'Гр_да_{message.from_user.id}_{message.reply_to_message.from_user.id}_{president_info["president_country"]}')
                    but_no = types.InlineKeyboardButton(text='Отказаться',
                                                        callback_data=f'Гр_нет_{message.from_user.id}_{message.reply_to_message.from_user.id}_{president_info["president_country"]}')
                    key.add(but_no, but_yes)
                    await bot.send_message(message.chat.id,
                                           text=f'Внимание, {await username(message.reply_to_message)}, президент страны {president_info["president_country"]} хочет сделать вас гражданином своей страны',
                                           reply_markup=key, parse_mode='HTML')
                else:
                    await bot.send_message(message.chat.id,
                                           f'{await username(message)}, в вашей стране максимум населения!',
                                           parse_mode='HTML')
            else:
                await bot.send_message(message.chat.id,
                                       f'{await username(message.reply_to_message)} уже является гражданином страны!',
                                       parse_mode='HTML')


# /mycitizens Граждане страны
async def mycitizens(message):
    await message.delete()
    data = []
    president_info = database.users.find_one({'id': message.from_user.id})
    if president_info['president_country'] != 'нет':
        citizens = list(database.users.find({'citizen_country': president_info['president_country']}))
        if len(citizens) <= 1:
            await bot.send_message(message.chat.id,
                                   f'{await username(message)}, у вас нет граждан\n'
                                   f'Чтобы взять кого-то, напишите "Взять гражданина" в ответ на его сообщение',
                                   parse_mode='HTML')
        else:
            for i in range(0, len(citizens)):
                user_id = citizens[i]['id']
                userna = citizens[i]['username']
                data.append(f'{i + 1}. {await username_2(user_id, userna)} - {citizens[i]["job"]}\n')
            await bot.send_message(message.chat.id, f'👨‍👩‍👧‍👧 Список граждан {await username(message)}:\n' + ''.join(data),
                               parse_mode='HTML')


# /nalog Установить налог для государства
async def nalog(message):
    await message.delete()
    president_info = database.users.find_one({'id': message.from_user.id})
    if president_info['president_country'] != 'нет':
        nalog_amount = message.get_args().split()
        try:
            nalog = int(nalog_amount[0])
            if nalog <= 100 and nalog >= 0:
                database.countries.update_one({'country': president_info['president_country']},
                                              {'$set': {'nalog_job': nalog}})

                await bot.send_message(message.chat.id,
                                       f'Теперь налог на работу в стране {president_info["president_country"]} составляет: {nalog}%')
            else:
                await bot.send_message(message.chat.id, f'Налог может составлять от 0 до 100')

        except:
            await bot.send_message(message.chat.id,
                                   f'{await username(message)}, налог вводится по примеру /nalog 10 (налог будет составлять 10%)',
                                   parse_mode='HTML')
    else:
        await bot.send_message(message.chat.id,
                               f'{await username(message)}, только президент может так', parse_mode='HTML')


# /ccash Взаимодействие с деньгами страны
async def ccash(message: types.Message):
    await message.delete()
    president_info = database.users.find_one({'id': message.from_user.id})
    if president_info['president_country'] != 'нет':
        amount = message.get_args().split()
        try:
            if '-' in amount[0]:
                try:
                    cash = int(amount[0].replace('-', '', 1))
                    country_info = database.countries.find_one({'president': message.from_user.id})
                    if country_info['cash'] >= cash:
                        database.countries.update_one({'president': message.from_user.id},
                                                      {'$set': {'cash': country_info['cash'] - cash}})
                        database.users.update_one({'id': message.from_user.id}, {'$set': {'cash': president_info['cash'] + cash}})
                        await bot.send_message(message.chat.id,
                                               f'{await username(message)}, успешно взял из казны государства {cash}$ 💰',
                                               parse_mode='HTML')
                    else:
                        await bot.send_message(message.chat.id,
                                               f'{await username(message)}, в казне нет столько денег 💰',
                                               parse_mode='HTML')
                except:
                    await bot.send_message(message.chat.id,
                                           f'{await username(message)}, некорректно введена сумма ❌',
                                           parse_mode='HTML')

            elif '+' in amount[0]:
                try:
                    cash = int(amount[0].replace('+', '', 1))
                    country_info = database.countries.find_one({'president': message.from_user.id})
                    if president_info['cash'] >= cash:
                        database.countries.update_one({'president': message.from_user.id},
                                                      {'$set': {'cash': country_info['cash'] + cash}})
                        database.users.update_one({'id': message.from_user.id}, {'$set':  {'cash': president_info['cash'] - cash}})
                        await bot.send_message(message.chat.id,
                                               f'{await username(message)}, успешно положил в казну государства {cash}$ 💰',
                                               parse_mode='HTML')
                    else:
                        await bot.send_message(message.chat.id,
                                               f'{await username(message)}, у вас нет столько денег 💰',
                                               parse_mode='HTML')
                except:
                    await bot.send_message(message.chat.id,
                                           f'{await username(message)}, некорректно введена сумма ❌',
                                           parse_mode='HTML')
            else:
                await bot.send_message(message.chat.id, f'/ccash +10 - ложит деньги в казну 💰\n'
                                                        f'/ccash -10 - забирает деньги из казны 💰')
        except IndexError:
            await bot.send_message(message.chat.id, f'/ccash +10 - ложит деньги в казну 💰\n'
                                                    f'/ccash -10 - забирает деньги из казны 💰')


# /cpass О стране в которой ты президент
async def cpass(message):
    await check_user(message)
    president_info = database.users.find_one({'id': message.from_user.id})
    if president_info['president_country'] != 'нет':

        country_info = database.countries.find_one({'country': president_info['president_country']})

        citizens = database.users.find({'citizen_country': president_info['president_country']})
        await bot.send_photo(message.chat.id, photo=InputFile(
            f'{os.getcwd()}/res/country_pic/{president_info["president_country"]}.png'),
                             caption='📑 О стране: 📑\n'
                                     f'~{country_info["country"]}~\n'
                                     f'👱‍♂️ Президент: {await username(message)}\n'
                                     f'💰 Деньги в казне: {country_info["cash"]}$\n'
                                     f'🖤 Нефть: {country_info["oil"]} литров\n'
                                     f'🍔 Пища: {country_info["food"]} кг\n'
                                     f'⛓ Территория: {country_info["territory"]} км\n'
                                     f'🎖 Уровень: {country_info["level"]}\n'
                                     f'👨‍👩‍👧‍👦 Население: {len(list(citizens))} из {country_info["max_people"]} чел.\n'
                                     f'🧑‍🌾 Территория фермеров: {country_info["terr_for_farmers"]} км\n'
                                     f'💵 Налог на работу: {country_info["nalog_job"]}%\n'
                                     f'💸 Стоимость: {country_info["cost"]} $\n', parse_mode='HTML')
    else:
        await bot.send_message(message.chat.id, f'{await username(message)}, вы не являетесь президентом какой-либо страны', parse_mode='HTML')


# /sell_country Продажа страны
async def sell_country(message):
    await check_user(message)
    president_info = database.users.find_one({'id': message.from_user.id})

    if president_info['president_country'] != 'нет':
        country_info = database.countries.find_one({'country': president_info['president_country']})
        key = InlineKeyboardMarkup()
        but1 = InlineKeyboardButton('Да',
                                    callback_data=f'sell_country_{message.from_user.id}_{president_info["president_country"]}_{round(country_info["cost"] * 0.1)}')
        but2 = InlineKeyboardButton('Нет', callback_data=f'sell_country_no_{message.from_user.id}')
        key.add(but1, but2)
        await bot.send_message(message.chat.id,
                               f'{await username(message)}, вы действительно хотите продать {president_info["president_country"]}?\n'
                               f'Вы получите {round(country_info["cost"] * 0.1)}$',
                               reply_markup=key, parse_mode='HTML')
    else:
        await bot.send_message(message.chat.id, f'{await username(message)}, вы не являетесь президентом какой-либо страны', parse_mode='HTML')


def register_handlers_get_citizen(dp: Dispatcher):
    dp.register_message_handler(get_citizen, content_types='text',
                                text=['/get_citizen', 'Взять гражданина', 'взять гражданина'])
    dp.register_message_handler(nalog, commands='nalog')
    dp.register_message_handler(mycitizens,
                                text=['Мои граждане', 'мои граждане', 'Граждане', 'граждане', '/mycitizens'])
    dp.register_message_handler(ccash, commands='ccash')
    dp.register_message_handler(cpass, content_types='text',
                                text=['О стране', 'о стране', 'моя страна', 'Моя страна', '/cpass'])
    dp.register_message_handler(sell_country, content_types='text',
                                text=['/sell_country', 'Продать страну', 'продать страну'])
