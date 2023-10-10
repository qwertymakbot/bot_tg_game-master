from bot import Dispatcher, check_user, database
import datetime
import random
from create_bot import bot
from bot import username

# Бонус
async def bonus(message):
    await check_user(message)
    members = await bot.get_chat_member(chat_id=-1001879290440, user_id=message.from_user.id)

    if members['status'] != 'left':
        bonus_info = database.bonus.find_one({'id': message.from_user.id})
        if bonus_info is None:
            now = datetime.datetime.now()
            database.bonus.insert_one({
                'id': message.from_user.id,
                'date': now.day
            })
            rnd_cash = random.randint(1000, 100000)
            user_info = database.users.find_one({'id': message.from_user.id})
            database.users.update_one({'id': message.from_user.id}, {'$set': {'cash': user_info['cash'] + rnd_cash}})
            await bot.send_message(message.chat.id,
                                   f'{await username(message)}, ваш бонус на сегодняшний день {rnd_cash}$', parse_mode='HTML')
        else:
            now = datetime.datetime.now()
            if now.day == bonus_info['date']:
                await bot.send_message(message.chat.id, f'{await username(message)}, вы уже получали сегодня бонус!', parse_mode='HTML')
            else:
                now = datetime.datetime.now()
                database.bonus.update_one({'id': message.from_user.id}, {'$set': {'date': now.day}})
                rnd_cash = random.randint(1000, 30000)
                user_info = database.users.find_one({'id': message.from_user.id})
                database.users.update_one({'id': message.from_user.id},
                                          {'$set': {'cash': user_info['cash'] + rnd_cash}})
                await bot.send_message(message.chat.id,
                                       f'{await username(message)}, ваш бонус на сегодняшний день {rnd_cash}$', parse_mode='HTML')
    else:
        await bot.send_message(message.chat.id, f'{await username(message)}, чтобы получить бонус, вы должны состоять в моем канале @makbotinfo', parse_mode='HTML')


def register_handlers_bonus(dp: Dispatcher):
    dp.register_message_handler(bonus, commands='bonus')
    dp.register_message_handler(bonus, content_types='text', text=['Бонус', 'бонус'])
