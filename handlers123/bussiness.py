import json
import os

from bot import Dispatcher, database, types, username


async def sell_yes(callback: types.CallbackQuery):
    try:
        with open(f'game/sell_bus/{callback.from_user.id}.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            cost = data['cost']
            user_info = database.users.find_one({'id': callback.from_user.id})
            # добавление денег за продажу
            database.users.update_one({'id': callback.from_user.id}, {'$set': {'cash': user_info['cash'] + cost}})
            # удаление бизнеса из БД
            database.users_bus.delete_one({'id': callback.from_user.id})
            # удаление рабочих
            database.autocreater_work.delete_one({'boss': callback.from_user.id})



        os.remove(os.getcwd() + f'\game\sell_bus\{callback.from_user.id}.json')
        os.remove(os.getcwd() + f'\\game\\bus_workplace\\{callback.from_user.id}.json')
        await callback.answer(f'{await username(callback)}, вы успешно продали бизнес!', parse_mode='HTML')

    except:
        await callback.answer(f'{await username(callback)}, это предназначено не вам', parse_mode='HTML')


async def sell_no(callback: types.CallbackQuery):
    try:
        path = os.getcwd()
        os.remove(path + f'\game\sell_bus\{callback.from_user.id}')
        await callback.answer(f'{await username(callback)}, вы отказались от продажи', parse_mode='HTML')
    except:
        await callback.answer(f'{await username(callback)}, это предназначено не вам', parse_mode='HTML')


def register_handlers_bussiness(dp: Dispatcher):
    dp.register_callback_query_handler(sell_yes, text='Бизнес_продать')
    dp.register_callback_query_handler(sell_no, text='Бизнес_не_продать')
