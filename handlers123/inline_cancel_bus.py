import json
import os

from bot import Dispatcher, database, types, username, username_2
from create_bot import bot


async def cancel_yes(callback: types.CallbackQuery):
    try:
        with open(f'{os.getcwd()}/game/cancel_bus/{callback.from_user.id}.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            f.close()
            user_info = database.users.find_one({'id': callback.from_user.id})
            # Вычет ресурсов со счета государства
            country_info = database.contries.find_one({'country': user_info['citizen_country']})
            database.contries.update_one({'country': user_info["citizen_country"]}, {'$set':{'oil': country_info['oil'] - data['oil']/2,
                                                                                             'food': country_info['food'] - data['food']/2,
                                                                                             'cash': country_info['cash'] - data['cost']/2}})
            # Возвращение ресурсов на баланс
            database.users.update_one({'id': callback.from_user.id}, {'$set': {'oil': user_info['oil']+ data['oil']/2,
                                                                               'food': user_info['food']+ data['food']/2,
                                                                               'cash': user_info['cash']+ data['cost']/2}})
            # Выдача пол ЗП строителям
            amount = 0
            if len(data['builders']) != 0:  # Если есть строители
                builders_username = []
                for builder in data['builders']:
                    builder_info = database.users.find_one({'id': builder})
                    amount = amount + data['builder_pay'] / 2
                    # Вычет из баланса заказчика
                    database.users.update_one({'id': callback.from_user.id}, {'$set': {'cash': user_info['cash'] - data['builder_pay']/2}})
                    # Начисление на баланс строителя
                    database.users.update_one({'id': builder},
                                              {'$set': {'cash': builder_info['cash'] + data['builder_pay'] / 2}})
                    # Удаление строителей из БД
                    database.builders_work.delete_one({'builder': builder})
                    # Добавление ника в список
                    builders_username.append(f'{await username_2(builder, builder_info["username"])}')
                    # Удаление стройки build_bus
                    os.remove(f'{os.getcwd()}/game/build_bus/{callback.from_user.id}.json')
                await bot.send_message(callback.message.chat.id, text=f'{await username(callback)}, ваша стройка была успешно отменена!\n'
                                       f'⚙️ Вам было начислено следующее:\n'
                                       f'🖤 Нефть: +{round(data["oil"] / 2)}л\n'
                                       f'🍔 Еда: +{round(data["food"] / 2)}кг\n'
                                       f'💰 Деньги: +{round(data["cost"] / 2)}$\n'
                                       f'💸 Строителям суммарно было начислено: +{round(amount)}$\n'
                                       f'{"".join(builders_username)}', parse_mode='HTML')
            else:
                pass
    except:
        await callback.answer(f'{await username(callback)}, это предназначено не Вам!', parse_mode='HTML')


async def cancel_no(callback: types.CallbackQuery):
    try:
        os.remove(f'{os.getcwd()}/game/cancel_bus/{callback.from_user.id}.json')
        await callback.answer(f'{await username(callback)}, ваше решение было отменено!', parse_mode='HTML')
    except:
        await callback.answer(f'{await username(callback)}, это предназначено не Вам!', parse_mode='HTML')


def register_handlers_cancel_bus(dp: Dispatcher):
    dp.register_callback_query_handler(cancel_yes, text='Стройка_отмена_да')
    dp.register_callback_query_handler(cancel_no, text='Стройка_отмена_нет')
