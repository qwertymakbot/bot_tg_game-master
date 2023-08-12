import os

from bot import bot, check_user, database, res_database, types, InlineKeyboardButton, InlineKeyboardMarkup, username, Dispatcher


# /leave_creater Уйти с автосборки
async def leave_creater(message: types.Message):
    await check_user(message)
    res_job = res_database.job.find_one({'id': message.from_user.id})
    if not res_job['working']:  # Если не работает
        autocreater_info = database.autocreater_work.find_one({'creater': message.from_user.id})
        if autocreater_info is not None:  # Если устроен на предприятие
            # Удаление из док-та
            database.autocreater_work.delete_one({'creater': message.from_user.id})
            await bot.send_message(message.chat.id, f'{await username(message)}, вы успешно уволились с предприятия!', parse_mode='HTML')
        else:
            await bot.send_message(message.chat.id, f'{await username(message)}, вы не устроены на предприятие!', parse_mode='HTML')
    else:  # Если работает
        await bot.send_message(message.chat.id, f'{await username(message)}, для начала окончите работу!', parse_mode='HTML')


# /creater Автосборщик
async def creater(message: types.Message):
    await check_user(message)
    user_info = database.users.find_one({'id': message.from_user.id})
    if user_info['job'] == 'Автосборщик':
        autocreater_info = database.autocreater_work.find_one({'creater': message.from_user.id})
        if autocreater_info is None:  # Если не устроен на предприятие
            all_bus = list(database.users_bus.find({'$and': [{'name': 'Сборка авто'}, {'status': 'work'}, {'country': user_info['citizen_country']}]}))
            new_list_bus = []
            for bus in all_bus:
                all_autocreaters = database.autocreater_work.find({'boss': bus['boss']})
                if all_autocreaters < bus['work_place']:
                    new_list_bus.append(bus)
            key = InlineKeyboardMarkup()
            but_nazad = InlineKeyboardButton('◀️', callback_data=f'creater_nazad_')
            but_vpered = InlineKeyboardButton('▶️', callback_data=f'creater_vper_')
            accept = InlineKeyboardButton('Устроиться ✅', callback_data=f'creater_accept_')
            otmena = InlineKeyboardButton('Отмена ❌', callback_data=f'creater_otmena_')
            key.add(but_nazad, accept,but_vpered,otmena)
            await bot.send_message(f'Бизнес {new_list_bus[0]["name"]} {new_list_bus[0]["product"]}:\n'
                                   f'')


        else:
            await bot.send_message(message.chat.id, f'{await username(message)}, вы уже работаете на предприятии!')
    else:
        await bot.send_message(message.chat.id, f'{await username(message)}, данная команда доступна только Автосборщику')


# Регистрация хендлеров
def register_handlers_autocreater(dp: Dispatcher):
    dp.register_message_handler(leave_creater, commands='leave_creater')
    dp.register_message_handler(creater, commands='creater')
