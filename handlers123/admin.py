from bot import check_user, scheduler, Dispatcher, bot, types, tag_user, InputFile, InlineKeyboardButton, \
    InlineKeyboardMarkup, database, res_database, username, add_time_min, username_2
from create_bot import dp
import pytz
from datetime import datetime, timedelta
from pymongo.mongo_client import MongoClient
import os
# БД
database_adm = MongoClient(
    "mongodb+srv://maksemqwerty:maksem228@cluster0.mylnsur.mongodb.net/?retryWrites=true&w=majority").adminka

#
@dp.message_handler(commands='rules')
async def rules(message: types.Message):
    with open(f'{os.getcwd()}/res/rules.txt', 'r', encoding='utf-8') as f:
        txt = f.readlines()
        f.close()
    await message.reply(''.join(txt))


# Новый участник
@dp.message_handler(content_types=[types.ContentType.NEW_CHAT_MEMBERS])
async def new_members_handler(message: types.Message):
    await message.delete()
    new_member = message.new_chat_members[0]
    await bot.send_message(message.chat.id, f"Добро пожаловать, танкист {new_member.mention}\n"
                                            f'Ты попал в чатик по BLITZ, который объединяет игроков RU и EU регионов\n'
                                            f"Правила: /rules")
# Вышедший участник
@dp.message_handler(content_types=[types.ContentType.LEFT_CHAT_MEMBER])
async def lefy_members_handler(message: types.Message):
    await message.delete()

# Список админов
@dp.message_handler(content_types='text', text=['Админы', 'админы', 'Кто админ', 'кто админ'])
async def admins(message: types.Message):
    admins_list = list(database_adm.admins.find({'chat_id': message.chat.id}))
    admins_ml = []
    admins_st = []
    admins_creator = []
    for admin in admins_list:
        if admin['ml_admin']:
            user_info = database.users.find_one({'id': admin['id']})
            admins_ml.append(f'\n{await username_2(admin["id"], user_info["firstname"])}')
        elif admin['st_admin']:
            user_info = database.users.find_one({'id': admin['id']})
            admins_st.append(f'\n{await username_2(admin["id"], user_info["firstname"])}')
        elif admin['creator']:
            user_info = database.users.find_one({'id': admin['id']})
            admins_creator.append(f'{await username_2(admin["id"], user_info["firstname"])}\n')

    if admins_st:
        admins_st.append('\n')
        admins_creator.append('\n')
    await message.reply(f'Создатель ⭐️⭐️⭐️\n'
                        f'{"".join(admins_creator)}'
                        f'{"Старшие админы ⭐️⭐️" if admins_st else ""}'
                        f'{"".join(admins_st)}'
                        f'\n{"Младшие админы ⭐️" if admins_ml else ""}'
                        f'{"".join(admins_ml)}', parse_mode='HTML')


# Младший админ
@dp.message_handler(content_types='text', text='!админ')
async def ml_admin(message: types.Message):
    is_creator = await creator_check(message)
    if database_adm.admins.find_one({'$and': [{'id': message.from_user.id}, {'chat_id': message.chat.id}]}) is None:
        await bot.send_message(message.chat.id, f'{await username(message)}, у вас недостаточно прав!',
                               parse_mode='HTML')
        return
    is_st_admin = database_adm.admins.find_one({'$and': [{'id': message.from_user.id}, {'chat_id': message.chat.id}]})[
        'st_admin']
    if is_creator or is_st_admin:
        if message.reply_to_message:
            user_info = database_adm.admins.find_one(
                {'$and': [{'id': message.reply_to_message.from_user.id}, {'chat_id': message.chat.id}]})
            if user_info is None:
                database_adm.admins.insert_one({'id': message.reply_to_message.from_user.id,
                                                'ml_admin': True,
                                                'st_admin': False,
                                                'creator': False,
                                                'chat_id': message.chat.id})
                await bot.send_message(message.chat.id,
                                       f'{await username(message.reply_to_message)}, вы были повышены до Младшего админа\n'
                                       f'Действие совершил: {await username(message)}', parse_mode='HTML')
            elif user_info['creator']:
                await bot.send_message(message.chat.id, f'{await username(message)}, у вас недостаточно прав!',
                                       parse_mode='HTML')
                return
            elif user_info['st_admin']:
                database_adm.admins.update_one(
                    {'$and': [{'id': message.reply_to_message.from_user.id}, {'chat_id': message.chat.id}]},
                    {'$set': {'ml_admin': True,
                              'st_admin': False}})
                await bot.send_message(message.chat.id,
                                       f'{await username(message.reply_to_message)}, вы были понижены до Младшего админа\n'
                                       f'Действие совершил: {await username(message)}', parse_mode='HTML')
            elif user_info['ml_admin']:
                await bot.send_message(message.chat.id,
                                       f'{await username(message.reply_to_message)}, уже Младший админ',
                                       parse_mode='HTML')
            else:
                database_adm.admins.update_one(
                    {'$and': [{'id': message.reply_to_message.from_user.id}, {'chat_id': message.chat.id}]},
                    {'$set': {'ml_admin': True}})
                await bot.send_message(message.chat.id,
                                       f'{await username(message.reply_to_message)}, вы были повышены до Младшего админа\n'
                                       f'Действие совершил: {await username(message)}', parse_mode='HTML')
        else:
            await bot.send_message(message.chat.id,
                                   f'{await username(message)}, вам нужно ответить данной командой на сообщение пользователя!',
                                   parse_mode='HTML')
    else:
        await bot.send_message(message.chat.id, f'{await username(message)}, у вас недостаточно прав!',
                               parse_mode='HTML')


# Старший админ
@dp.message_handler(content_types='text', text='!!админ')
async def st_admin(message: types.Message):
    is_creator = await creator_check(message)
    if database_adm.admins.find_one({'$and': [{'id': message.from_user.id}, {'chat_id': message.chat.id}]}) is None:
        await bot.send_message(message.chat.id, f'{await username(message)}, у вас недостаточно прав!',
                               parse_mode='HTML')
        return
    if is_creator:
        if message.reply_to_message:
            user_info = database_adm.admins.find_one(
                {'$and': [{'id': message.reply_to_message.from_user.id}, {'chat_id': message.chat.id}]})
            if user_info is None:
                database_adm.admins.insert_one({'id': message.reply_to_message.from_user.id,
                                                'ml_admin': False,
                                                'st_admin': True,
                                                'creator': False,
                                                'chat_id': message.chat.id})
                await bot.send_message(message.chat.id,
                                       f'{await username(message.reply_to_message)}, вы были повышены до Младшего админа\n'
                                       f'Действие совершил: {await username(message)}', parse_mode='HTML')
            elif user_info['creator']:
                await bot.send_message(message.chat.id, f'{await username(message)}, у вас недостаточно прав!',
                                       parse_mode='HTML')
                return
            elif user_info['st_admin']:
                await bot.send_message(message.chat.id,
                                       f'{await username(message.reply_to_message)}, уже Старший админ',
                                       parse_mode='HTML')
            else:
                database_adm.admins.update_one(
                    {'$and': [{'id': message.reply_to_message.from_user.id}, {'chat_id': message.chat.id}]},
                    {'$set': {'st_admin': True,
                              'ml_admin': False}})
                await bot.send_message(message.chat.id,
                                       f'{await username(message.reply_to_message)}, вы были повышены до Старшего админа\n'
                                       f'Действие совершил: {await username(message)}', parse_mode='HTML')
        else:
            await bot.send_message(message.chat.id,
                                   f'{await username(message)}, вам нужно ответить данной командой на сообщение пользователя!',
                                   parse_mode='HTML')
    else:
        await bot.send_message(message.chat.id, f'{await username(message)}, у вас недостаточно прав!',
                               parse_mode='HTML')


# Разжаловать
@dp.message_handler(content_types='text', text=['Разжаловать', 'разжаловать'])
async def razjalov(message: types.Message):
    is_creator = await creator_check(message)
    is_st_admin = database_adm.admins.find_one({'$and': [{'id': message.from_user.id}, {'chat_id': message.chat.id}]})[
        'st_admin']
    if database_adm.admins.find_one({'$and': [{'id': message.from_user.id}, {'chat_id': message.chat.id}]}) is None:
        await bot.send_message(message.chat.id, f'{await username(message)}, у вас недостаточно прав!',
                               parse_mode='HTML')
        return
    if is_creator:
        if message.reply_to_message:
            user_info = database_adm.admins.find_one(
                {'$and': [{'id': message.reply_to_message.from_user.id}, {'chat_id': message.chat.id}]})
            if user_info is None:
                await bot.send_message(message.chat.id,
                                       f'{await username(message.reply_to_message)}, не является админом!',
                                       parse_mode='HTML')
            elif user_info['creator']:
                await bot.send_message(message.chat.id, f'{await username(message)}, у вас недостаточно прав!',
                                       parse_mode='HTML')
                return
            elif user_info['st_admin'] or user_info['ml_admin']:
                database_adm.admins.update_one(
                    {'$and': [{'id': message.reply_to_message.from_user.id}, {'chat_id': message.chat.id}]},
                    {'$set': {'ml_admin': False,
                              'st_admin': False}})
                await bot.send_message(message.chat.id,
                                       f'{await username(message.reply_to_message)}, вы были разжалованы!\n'
                                       f'Действие совершил: {await username(message)}', parse_mode='HTML')
            else:
                await bot.send_message(message.chat.id,
                                       f'{await username(message.reply_to_message)}, не является админом!',
                                       parse_mode='HTML')
        else:
            await bot.send_message(message.chat.id,
                                   f'{await username(message)}, вам нужно ответить данной командой на сообщение пользователя!',
                                   parse_mode='HTML')
        return
    if is_st_admin:
        if message.reply_to_message:
            user_info = database_adm.admins.find_one(
                {'$and': [{'id': message.reply_to_message.from_user.id}, {'chat_id': message.chat.id}]})
            if user_info['creator']:
                await bot.send_message(message.chat.id, f'{await username(message)}, у вас недостаточно прав!',
                                       parse_mode='HTML')
                return
            if user_info['ml_admin']:
                database_adm.admins.update_one(
                    {'$and': [{'id': message.reply_to_message.from_user.id}, {'chat_id': message.chat.id}]},
                    {'$set': {'ml_admin': False}})
                await bot.send_message(message.chat.id,
                                       f'{await username(message.reply_to_message)}, вы были разжалованы!\n'
                                       f'Действие совершил: {await username(message)}', parse_mode='HTML')
            elif user_info['st_admin']:
                await bot.send_message(message.chat.id, f'{await username(message)}, у вас недостаточно прав!',
                                       parse_mode='HTML')
            else:
                await bot.send_message(message.chat.id,
                                       f'{await username(message.reply_to_message)}, не является админом!',
                                       parse_mode='HTML')
        else:
            await bot.send_message(message.chat.id,
                                   f'{await username(message)}, вам нужно ответить данной командой на сообщение пользователя!',
                                   parse_mode='HTML')

# Выдать мут
@dp.message_handler(commands='мут', commands_prefix='!')
async def mute(message: types.Message):
    try:
        date, reason = str(message.text).replace('!мут ', '').split('\n')
        is_creator = await creator_check(message)
        if database_adm.admins.find_one({'$and': [{'id': message.from_user.id}, {'chat_id': message.chat.id}]}) is None:
            await bot.send_message(message.chat.id, f'{await username(message)}, у вас недостаточно прав!',
                                   parse_mode='HTML')
            return
        is_st_admin = \
        database_adm.admins.find_one({'$and': [{'id': message.from_user.id}, {'chat_id': message.chat.id}]})[
            'st_admin']
        is_ml_admin = \
        database_adm.admins.find_one({'$and': [{'id': message.from_user.id}, {'chat_id': message.chat.id}]})[
            'ml_admin']
        if is_creator or is_st_admin or is_ml_admin:
            if message.reply_to_message:
                is_st_admin = \
                    database_adm.admins.find_one(
                        {'$and': [{'id': message.reply_to_message.from_user.id}, {'chat_id': message.chat.id}]})
                is_ml_admin = \
                    database_adm.admins.find_one(
                        {'$and': [{'id': message.reply_to_message.from_user.id}, {'chat_id': message.chat.id}]})
                is_creator_reply = \
                    database_adm.admins.find_one(
                        {'$and': [{'id': message.reply_to_message.from_user.id}, {'chat_id': message.chat.id}]})
                # Если нету пользователя в админах то мут
                if is_st_admin is None:
                    if 'мин' in date.split(' ')[1]:
                        tz = pytz.timezone('Etc/GMT-3')
                        minute = int(date.split(' ')[0])
                        time = datetime.now(tz=tz) + timedelta(minutes=minute)
                        await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id,
                                                       types.ChatPermissions(False), until_date=time)
                    elif 'ч' in date.split(' ')[1]:
                        tz = pytz.timezone('Etc/GMT-3')
                        hours = int(date.split(' ')[0])
                        time = datetime.now(tz=tz) + timedelta(hours=hours)
                        await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id,
                                                       types.ChatPermissions(False), until_date=time)
                    elif 'д' in date.split(' ')[1]:
                        tz = pytz.timezone('Etc/GMT-3')
                        days = int(date.split(' ')[0])
                        time = datetime.now(tz=tz) + timedelta(days=days)
                        await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id,
                                                       types.ChatPermissions(False), until_date=time)
                    else:
                        tz = pytz.timezone('Etc/GMT-3')
                        minute = 10
                        time = datetime.now(tz=tz) + timedelta(minutes=minute)
                        await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id,
                                                       types.ChatPermissions(False), until_date=time)
                    await bot.send_message(message.chat.id,
                                           f'{await username(message)}, выдал мут {await username(message.reply_to_message)} на {date} по причине {reason}',
                                           parse_mode='HTML')
                    await log(message, message.reply_to_message.from_user.id, 'мут', date, reason)
                # Если создатель - выдает мут любому
                elif is_creator:
                    if 'мин' in date.split(' ')[1]:
                        tz = pytz.timezone('Etc/GMT-3')
                        minute = int(date.split(' ')[0])
                        time = datetime.now(tz=tz) + timedelta(minutes=minute)
                        await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id,
                                                       types.ChatPermissions(False), until_date=time)
                    elif 'ч' in date.split(' ')[1]:
                        tz = pytz.timezone('Etc/GMT-3')
                        hours = int(date.split(' ')[0])
                        time = datetime.now(tz=tz) + timedelta(days=hours)
                        await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id,
                                                       types.ChatPermissions(False), until_date=time)
                    elif 'д' in date.split(' ')[1]:
                        tz = pytz.timezone('Etc/GMT-3')
                        days = int(date.split(' ')[0])
                        time = datetime.now(tz=tz) + timedelta(days=days)
                        await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id,
                                                       types.ChatPermissions(False), until_date=time)
                    else:
                        tz = pytz.timezone('Etc/GMT-3')
                        minute = 10
                        time = datetime.now(tz=tz) + timedelta(minutes=minute)
                        await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id,
                                                       types.ChatPermissions(False), until_date=time)
                    await bot.send_message(message.chat.id,
                                           f'{await username(message)}, выдал мут {await username(message.reply_to_message)} на {date} по причине {reason}',
                                           parse_mode='HTML')
                    await log(message, message.reply_to_message.from_user.id, 'мут', date, reason)
                # Если мут кого то из админов
                elif is_creator_reply['creator'] or is_st_admin['st_admin'] or is_ml_admin['ml_admin']:
                    await bot.send_message(message.chat.id, f'{await username(message)}, у вас недостаточно прав!',
                                           parse_mode='HTML')
                    # Выдача бывшим админам мута
                else:
                    print(message.get_args())
            else:
                await bot.send_message(message.chat.id,
                                       f'{await username(message)}, вам нужно ответить данной командой на сообщение пользователя!',
                                       parse_mode='HTML')
        else:
            await bot.send_message(message.chat.id, f'{await username(message)}, у вас недостаточно прав!',
                                   parse_mode='HTML')
    except:
        await bot.send_message(message.chat.id, f'{await username(message)}, укажите причину и время мута!',
                               parse_mode='HTML')

# Снять мут
@dp.message_handler(commands=['анмут', 'размутить'], commands_prefix='!')
async def unmute(message: types.Message):
    is_creator = await creator_check(message)
    if database_adm.admins.find_one({'$and': [{'id': message.from_user.id}, {'chat_id': message.chat.id}]}) is None:
        await bot.send_message(message.chat.id, f'{await username(message)}, у вас недостаточно прав!',
                               parse_mode='HTML')
        return
    is_st_admin = database_adm.admins.find_one({'$and': [{'id': message.from_user.id}, {'chat_id': message.chat.id}]})[
        'st_admin']
    is_ml_admin = database_adm.admins.find_one({'$and': [{'id': message.from_user.id}, {'chat_id': message.chat.id}]})[
        'ml_admin']
    if is_creator or is_st_admin or is_ml_admin:
        if message.reply_to_message:
            is_st_admin = \
                database_adm.admins.find_one(
                    {'$and': [{'id': message.reply_to_message.from_user.id}, {'chat_id': message.chat.id}]})
            is_ml_admin = \
                database_adm.admins.find_one(
                    {'$and': [{'id': message.reply_to_message.from_user.id}, {'chat_id': message.chat.id}]})
            is_creator_reply = \
                database_adm.admins.find_one(
                    {'$and': [{'id': message.reply_to_message.from_user.id}, {'chat_id': message.chat.id}]})
            # Если нету пользователя в админах то мут
            if is_st_admin is None:
                await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id,
                                               types.ChatPermissions(can_send_messages=True,
                                                                     can_send_media_messages=True,
                                                                     can_send_other_messages=True,
                                                                     can_add_web_page_previews=True,
                                                                     can_invite_users=True))
                await bot.send_message(message.chat.id,
                                       f'{await username(message)}, снял мут с {await username(message.reply_to_message)}',
                                       parse_mode='HTML')
                await log_unmute(message, message.reply_to_message.from_user.id)
            # Если создатель - выдает мут любому
            elif is_creator:
                await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id,
                                               types.ChatPermissions(can_send_messages=True,
                                                                     can_send_media_messages=True,
                                                                     can_send_other_messages=True,
                                                                     can_add_web_page_previews=True,
                                                                     can_invite_users=True))
                await bot.send_message(message.chat.id,
                                       f'{await username(message)}, снял мут с {await username(message.reply_to_message)}',
                                       parse_mode='HTML')
                await log_unmute(message, message.reply_to_message.from_user.id)
            # Если мут кого то из админов
            elif is_creator_reply['creator'] or is_st_admin['st_admin'] or is_ml_admin['ml_admin']:
                await bot.send_message(message.chat.id, f'{await username(message)}, у вас недостаточно прав!',
                                       parse_mode='HTML')
                # Выдача бывшим админам мута
            else:
                print(message.get_args())
        else:
            await bot.send_message(message.chat.id,
                                   f'{await username(message)}, вам нужно ответить данной командой на сообщение пользователя!',
                                   parse_mode='HTML')
    else:
        await bot.send_message(message.chat.id, f'{await username(message)}, у вас недостаточно прав!',
                               parse_mode='HTML')

# Выдать бан
@dp.message_handler(commands=['бан'], commands_prefix='!')
async def ban(message: types.Message):
        print(123)
        reason = str(message.text).replace('!бан ', '')
        if '!бан' in reason:
            await bot.send_message(message.chat.id, f'{await username(message)}, укажите причину бана!',
                                   parse_mode='HTML')
            return
        is_creator = await creator_check(message)
        if database_adm.admins.find_one({'$and': [{'id': message.from_user.id}, {'chat_id': message.chat.id}]}) is None:
            await bot.send_message(message.chat.id, f'{await username(message)}, у вас недостаточно прав!',
                                   parse_mode='HTML')
            return
        is_st_admin = \
        database_adm.admins.find_one({'$and': [{'id': message.from_user.id}, {'chat_id': message.chat.id}]})[
            'st_admin']
        is_ml_admin = \
        database_adm.admins.find_one({'$and': [{'id': message.from_user.id}, {'chat_id': message.chat.id}]})[
            'ml_admin']
        if is_creator or is_st_admin or is_ml_admin:
            if message.reply_to_message:
                is_st_admin = \
                    database_adm.admins.find_one(
                        {'$and': [{'id': message.reply_to_message.from_user.id}, {'chat_id': message.chat.id}]})
                is_ml_admin = \
                    database_adm.admins.find_one(
                        {'$and': [{'id': message.reply_to_message.from_user.id}, {'chat_id': message.chat.id}]})
                is_creator_reply = \
                    database_adm.admins.find_one(
                        {'$and': [{'id': message.reply_to_message.from_user.id}, {'chat_id': message.chat.id}]})
                # Если нету пользователя в админах то мут
                if is_st_admin is None:
                    await bot.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                    await bot.send_message(message.chat.id,
                                           f'{await username(message)}, выдал бан {await username(message.reply_to_message)} на ♾ по причине {reason}',
                                           parse_mode='HTML')
                    await log(message, message.reply_to_message.from_user.id, 'бан', '♾', reason)
                # Если создатель - выдает мут любому
                elif is_creator:
                    await bot.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                    await bot.send_message(message.chat.id,
                                           f'{await username(message)}, выдал бан {await username(message.reply_to_message)} на ♾ по причине {reason}',
                                           parse_mode='HTML')
                    await log(message, message.reply_to_message.from_user.id, 'бан', '♾', reason)
                # Если мут кого то из админов
                elif is_creator_reply['creator'] or is_st_admin['st_admin'] or is_ml_admin['ml_admin']:
                    await bot.send_message(message.chat.id, f'{await username(message)}, у вас недостаточно прав!',
                                           parse_mode='HTML')
                    # Выдача бывшим админам мута
                else:
                    print(message.get_args())
            else:
                await bot.send_message(message.chat.id,
                                       f'{await username(message)}, вам нужно ответить данной командой на сообщение пользователя!',
                                       parse_mode='HTML')
        else:
            await bot.send_message(message.chat.id, f'{await username(message)}, у вас недостаточно прав!',
                                   parse_mode='HTML')

# Проверка создатель или нет
async def creator_check(message: types.Message):
    creator_info = await bot.get_chat_member(message.chat.id, message.from_user.id)
    creator = database_adm.admins.find_one({'$and': [{'id': message.from_user.id}, {'chat_id': message.chat.id}]})
    if creator is None and creator_info['status'] == 'creator':
        database_adm.admins.insert_one({'id': message.from_user.id,
                                        'ml_admin': False,
                                        'st_admin': False,
                                        'creator': True,
                                        'chat_id': message.chat.id})
        return True
    elif creator is None:
        return False
    elif creator['creator']:
        return True
    else:
        return False


# LOG
async def log(message, user_id, action, time, reason):
    if message.chat.id != -1001529344518:
        return
    user_info = database.users.find_one({'id': user_id})
    await bot.send_message(-1001564368973,
                           f'[{await username(message)}|@{message.from_user.username}], выдал {action} [{await username_2(user_id, user_id)}|@{user_info["username"]}] на {time}\n'
                           f'Причина: {reason}', parse_mode='HTML')


async def log_unmute(message, user_id):
    if message.chat.id != -1001529344518:
        return
    user_info = database.users.find_one({'id': user_id})
    await bot.send_message(-1001564368973,
                           f'[{await username(message)}|@{message.from_user.username}], снял мут [{await username_2(user_id, user_id)}|@{user_info["username"]}]',
                           parse_mode='HTML')
