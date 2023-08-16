from bot import check_user, scheduler, Dispatcher, bot, types, tag_user, InputFile, InlineKeyboardButton, \
    InlineKeyboardMarkup, database, res_database, username, add_time_min, username_2
from create_bot import dp
import pytz
from datetime import datetime


@dp.message_handler(content_types='text', text=['Автошкола', 'автошкола'])
async def autoschool(message: types.Message):
    await check_user(message)
    autoschool_info = res_database.autoschool.find_one({'id': message.from_user.id})
    if database.education.find_one({'id': message.from_user.id})['auto_school'] == 'да':
        await bot.send_message(message.chat.id, f'{await username(message)}, у вас уже есть категория B',
                               parse_mode='HTML')
        return
    if autoschool_info is not None:
        # Получение переменных с строки
        tz = pytz.timezone('Etc/GMT-3')
        date, time = autoschool_info['time'].split(' ')
        year, month, day = date.split('-')
        hour, minute, second = time.split(':')
        time_job = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
        time_now = datetime(datetime.now(tz=tz).year, datetime.now(tz=tz).month,
                            datetime.now(tz=tz).day, datetime.now(tz=tz).hour,
                            datetime.now(tz=tz).minute, datetime.now(tz=tz).second)
        result = time_job - time_now
        # Если уже отработал
        if '-' in str(result):
            await end_autoschool(message.from_user.id)
        else:
            await bot.send_message(message.chat.id,
                                   f'{await username(message)}, вы уже обучаетесь, вам ещё осталось {str(result).replace("days", "дней")}',
                                   parse_mode='HTML')
        return
    key = InlineKeyboardMarkup()
    key_yes = InlineKeyboardButton('Да ✅', callback_data=f'autoschl_yes_{str(message.from_user.id)[-3::]}')
    key_no = InlineKeyboardButton('Нет ❌', callback_data=f'autoschl_no_{str(message.from_user.id)[-3::]}')
    key.add(key_yes, key_no)
    await bot.send_message(message.chat.id, f'{await username(message)}, стоимость обучения на категорию B:\n'
                                            f'    - 1 000 000 $\n'
                                            f'    - 50 000 опыта\n'
                                            f'    - 7 500 кг еды\n'
                                            f'    - 1 000 л топлива\n'
                                            f'❗️ Обучение будет длиться 3 дня\n\n'
                                            f'Желаете начать обучение?', reply_markup=key, parse_mode='HTML')


@dp.callback_query_handler(lambda callback: 'autoschl_yes_' in callback.data)
async def autoschool_yes(callback: types.CallbackQuery):
    if callback.data.replace('autoschl_yes_', '') == str(callback.from_user.id)[-3::]:
        tz = pytz.timezone('Etc/GMT-3')
        # Добавление в бд инфы о болезни
        res_database.autoschool.insert_one({'id': callback.from_user.id,
                                            'time': await add_time_min(4320)})
        scheduler.add_job(end_autoschool, "date",
                          run_date=await add_time_min(4320),
                          args=(callback.from_user.id,), timezone=tz)
        await bot.send_message(callback.message.chat.id,
                               f'{await username(callback)}, вы начали обучение, через 3 дня вы закончите!',
                               parse_mode='HTML')
    else:
        await callback.answer('Это предназначено не вам!')


@dp.callback_query_handler(lambda callback: 'autoschl_no_' in callback.data)
async def autoschool_no(callback: types.CallbackQuery):
    if callback.data.replace('autoschl_no_', '') == str(callback.from_user.id)[-3::]:
        await callback.message.delete()
    else:
        await callback.answer('Это предназначено не вам!')


async def end_autoschool(user_id):
    database.education.update_one({'id': user_id}, {'$set': {'auto_school': 'да'}})
    user_info = database.users.find_one({"id": user_id})
    res_database.autoschool.delete_one({'id': user_id})
    await bot.send_message(user_id,
                           f'{await username_2(user_id, user_info["firstname"])}, вы окончили обучение на B категорию!',
                           parse_mode='HTML')
