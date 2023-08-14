from bot import check_user, types, InlineKeyboardButton, InlineKeyboardMarkup, database, bot, username, Dispatcher




# /shop Магазин

async def shop(message: types.Message):
    await check_user(message)
    user_info = database.users.find_one({'id': message.from_user.id})
    if user_info["citizen_country"] != 'нет':  # Если гражданин
        key = types.InlineKeyboardMarkup(row_width=1)
        # Категории в магазине
        cars = types.InlineKeyboardButton(text='Машины 🚗', callback_data='Магазин_машины')
        cases = types.InlineKeyboardButton(text='Кейсы 🎁', callback_data='Кейсы')
        marketplace = InlineKeyboardButton(text='Маркетплейс 💎', callback_data='marketplace_')
        key.add(cars, cases, marketplace)

        await bot.send_message(message.chat.id,
                               f'{await username(message)}, выберите категорию!', reply_markup=key, parse_mode='HTML')

    else:
        await bot.send_message(message.chat.id,
            f'{await username(message)}, для начала вам нужно стать гражданином какой-либо страны!', parse_mode='HTML')

def register_handlers_shop(dp: Dispatcher):
    dp.register_message_handler(shop, text=['Магазин', 'магазин'])
    dp.register_message_handler(shop, commands='shop')
