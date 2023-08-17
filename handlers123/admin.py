from bot import check_user, scheduler, Dispatcher, bot, types, tag_user, InputFile, InlineKeyboardButton, \
    InlineKeyboardMarkup, database, res_database, username, add_time_min, username_2
from create_bot import dp
import pytz

from pymongo.mongo_client import MongoClient

# БД
database_adm = MongoClient(
    "mongodb+srv://maksemqwerty:maksem228@cluster0.mylnsur.mongodb.net/?retryWrites=true&w=majority").adminka

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
                database_adm.admins.update_one({'$and': [{'id': message.reply_to_message.from_user.id}, {'chat_id': message.chat.id}]},
                                               {'$set': {'ml_admin': True,
                                                         'st_admin': False}})
                await bot.send_message(message.chat.id,
                                       f'{await username(message.reply_to_message)}, вы были понижены до Младшего админа\n'
                                       f'Действие совершил: {await username(message)}', parse_mode='HTML')
            elif user_info['ml_admin']:
                await bot.send_message(message.chat.id,
                                       f'{await username(message.reply_to_message)}, уже Младший админ', parse_mode='HTML')
            else:
                database_adm.admins.update_one({'$and': [{'id': message.reply_to_message.from_user.id}, {'chat_id': message.chat.id}]},
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
                                       f'{await username(message.reply_to_message)}, уже Старший админ', parse_mode='HTML')
            else:
                database_adm.admins.update_one({'$and': [{'id': message.reply_to_message.from_user.id}, {'chat_id': message.chat.id}]},
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
                await bot.send_message(message.chat.id, f'{await username(message.reply_to_message)}, вы были разжалованы!\n'
                                                        f'Действие совершил: {await username(message)}', parse_mode='HTML')
            else:
                await bot.send_message(message.chat.id, f'{await username(message.reply_to_message)}, не является админом!', parse_mode='HTML')
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

@dp.message_handler(commands='мут', commands_prefix='!')
async def mute(message: types.Message):
    print(message.get_args())
    try:
        date, reason = str(message.text).replace('!мут ','').split('\n')
        print(date)
        print(reason)
        is_creator = await creator_check(message)
        is_st_admin = database_adm.admins.find_one({'$and': [{'id': message.from_user.id}, {'chat_id': message.chat.id}]})[
            'st_admin']
        is_ml_admin = database_adm.admins.find_one({'$and': [{'id': message.from_user.id}, {'chat_id': message.chat.id}]})[
            'ml_admin']
        if is_creator or is_st_admin or is_ml_admin:
            if message.reply_to_message:
                is_st_admin = \
                database_adm.admins.find_one({'$and': [{'id': message.reply_to_message.from_user.id}, {'chat_id': message.chat.id}]})
                is_ml_admin = \
                database_adm.admins.find_one({'$and': [{'id': message.reply_to_message.from_user.id}, {'chat_id': message.chat.id}]})
                is_creator_reply = \
                    database_adm.admins.find_one(
                        {'$and': [{'id': message.reply_to_message.from_user.id}, {'chat_id': message.chat.id}]})
                # Если нету пользователя в админах то мут
                if is_st_admin is None:
                    print(205)
                # Если создатель - выдает мут любому
                elif is_creator:
                    await bot.send_message(message.chat.id, f'{await username(message)}, выдал мут {await username(message.reply_to_message)} на {date} по причине {reason}', parse_mode='HTML')
                # Если мут кого то из админов
                elif is_creator_reply['creator'] or is_st_admin['st_admin'] or is_ml_admin['ml_admin']:
                    await bot.send_message(message.chat.id,f'{await username(message)}, у вас недостаточно прав!', parse_mode='HTML')
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
