from bot import check_user, types, InlineKeyboardButton, InlineKeyboardMarkup, database, bot, username, Dispatcher


# Список машин
async def cars(callback: types.CallbackQuery):
    await check_user(callback)
    key = InlineKeyboardMarkup(2)
    user_info = database.users.find_one({'id': callback.from_user.id})
    if user_info['citizen_country'] != 'нет':
        cars_list = list(database.cars.find({'country': user_info['citizen_country']}))
        for i in range(0, len(cars_list)):
            car = InlineKeyboardButton(text=f'{cars_list[i]["name_car"]} Цена: {cars_list[i]["cost"]}$',
                                       callback_data=f'shop_{cars_list[i]["name_car"]}')
            key.add(car)
        await bot.send_message(callback.message.chat.id,
                               text=f'{await username(callback)}, вам доступны следующие машины!', reply_markup=key,
                               parse_mode='HTML')
    else:
        await bot.send_message(callback.message.chat.id,
                               text=f'{await username(callback)}, вы не являетесь гражданином (/citizen)',
                               parse_mode='HTML')


def register_handlers_shop(dp: Dispatcher):
    dp.register_callback_query_handler(cars, text='Магазин_машины')
