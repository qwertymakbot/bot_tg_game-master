from bot import *


# Список машин
async def cars(callback: types.CallbackQuery):
    await check_user(callback)
    user_id = callback.from_user.id
    with sqlite3.connect('game/data.db', timeout=10) as conn:
        cur = conn.cursor()
        key = InlineKeyboardMarkup(2)
        country = cur.execute("""SELECT citizen_country FROM users WHERE user_id = ?""",
                              (callback.from_user.id,)).fetchone()
        if country[0] != 'нет':
            cars_list = cur.execute("""SELECT name_car, cost FROM cars WHERE country = ?""", (country[0],)).fetchall()
            for i in range(0, len(cars_list)):
                car = InlineKeyboardButton(text=f'{cars_list[i][0]} Цена: {cars_list[i][1]}$',
                                           callback_data=f'shop_{cars_list[i][0]}')
                key.add(car)
            await bot.send_message(callback.message.chat.id, message_thread_id=callback.message.message_thread_id,
                                   text=f'@{callback.from_user.username}, вам доступны следующие машины!', reply_markup=key)
        else:
            await bot.send_message(callback.message.chat.id, message_thread_id=callback.message.message_thread_id,
                                   text=f'@{callback.from_user.username}, вы не являетесь гражданином (/citizen)')
        cur.close()

def register_handlers_shop(dp: Dispatcher):
    dp.register_callback_query_handler(cars, text='Магазин_машины')
