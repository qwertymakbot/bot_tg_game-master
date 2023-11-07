from bot import bot, username, username_2, res_database, database, Dispatcher, check_user, types, InlineKeyboardButton, InlineKeyboardMarkup


# /build Список объектов ожидающих строителей
async def build(message: types.Message):
    await check_user(message)
    user_info = database.users.find_one({'id': message.from_user.id})
    if user_info['job'] == 'Строитель':
        builder = database.builders_work.find_one({'builder': message.from_user.id})
        if builder is not None:
            await bot.send_message(message.chat.id, f'{await username(message)}, вы уже находитесь на стройке!', parse_mode='HTML')
            return
        all_building = list(database.users_bus.find({'$and': [{'status': 'need_builders'}, {'country': user_info['citizen_country']}]}))
        if not all_building:
            await bot.send_message(message.chat.id, f'{await username(message)}, в вашей стране нет строек!', parse_mode='HTML')
            return
        key = InlineKeyboardMarkup(row_width=3)
        but_nazad = InlineKeyboardButton('◀️', callback_data=f'build_naz_{str(message.from_user.id)[-3::]}_0')
        but_vpered = InlineKeyboardButton('▶️', callback_data=f'build_vper_{str(message.from_user.id)[-3::]}_0')
        but_ustroitsya = InlineKeyboardButton('Устроиться ✅', callback_data=f'build_ustr_{str(message.from_user.id)[-3::]}_0')
        but_otmena = InlineKeyboardButton('Отмена ❌', callback_data=f'build_otm_{str(message.from_user.id)[-3::]}')
        key.add(but_nazad, but_ustroitsya, but_vpered, but_otmena)
        all_builders = list(database.builders_work.find({'boss': all_building[0]['boss']}))
        await bot.send_message(message.chat.id, 'Бизнесы в режиме ожидания:'
                               f'{all_building[0]["name"]} {all_building[0]["product"]}\n'
                                f'Строителей на объекте: {len(all_builders)} из {all_building[0]["need_builder"]}\n'
                               f'Плата за стройку: {all_building[0]["bpay"]}\n\n'
                                                
                               f'Страница 1/{len(all_building)}', reply_markup=key)
    else:
        await bot.send_message(message.chat.id, f'{await username(message)}, это доступно только Строителю', parse_mode='HTML')


# /leave_build Уйти со стройки
async def leave_build(message: types.Message):
    await check_user(message)
    user_info = database.users.find_one({'id': message.from_user.id})
    if user_info['job'] == 'Строитель':
        bus_info = database.users_bus.find_one({'boss': database.builders_work.find_one({'builder': message.from_user.id})['boss']})
        if bus_info['status'] != 'building':
            key = InlineKeyboardMarkup()
            but_yes = InlineKeyboardButton('Да ✅', callback_data=f'leave_build_yes_{str(message.from_user.id)[-3::]}')
            but_no = InlineKeyboardButton('Нет ❌', callback_data=f'leave_build_no_{str(message.from_user.id)[-3::]}')
            key.add(but_yes, but_no)
            await bot.send_message(message.chat.id, f'{await username(message)}, вы уверены, что хотите уволиться с объекта {bus_info["name"]} {bus_info["product"]} ?', reply_markup=key, parse_mode='HTML')
        else:
            await bot.send_message(message.chat.id, f'{await username(message)}, вы не можете уволиться пока идёт стройка!', parse_mode='HTML')

    else:
        await bot.send_message(message.chat.id, f'{await username(message)}, данная команда доступна только Строителю!', parse_mode='HTML')


def register_handlers_stroitel(dp: Dispatcher):
    dp.register_message_handler(build, commands='build')
    dp.register_message_handler(leave_build, commands='leave_build')
