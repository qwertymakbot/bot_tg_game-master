from bot import bot, username, username_2, res_database, database, Dispatcher, check_user, types, InlineKeyboardButton, InlineKeyboardMarkup


# /build Список объектов ожидающих строителей
async def build(message: types.Message):
    await check_user(message)
    user_info = database.users.find_one({'id': message.from_user.id})
    if user_info['job'] == 'Строитель':
        builder = database.builders_work.find_one({'builder': message.from_user.id})
        if builder is not None:
            await bot.send_message(message.chat.id, f'{await username(message)}, вы уже находитесь на стройке!')
            return
        all_building = list(database.users_bus.find({'$and': [{'status': 'need_builders'}, {'country': user_info['citizen_country']}]}))
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
        await bot.send_message(message.chat.id, f'{await username(message)}, это доступно только Строителю')


# /leave_build Уйти со стройки
async def leave_build(message):
    await check_user(message)
    with sqlite3.connect('game/data.db', timeout=10) as conn:
        cur = conn.cursor()
        job = cur.execute("""SELECT job FROM users WHERE user_id = ?""", (message.from_user.id,)).fetchone()
        if job[0] == 'Строитель':
            boss = cur.execute("""SELECT boss FROM builders_work WHERE builder = ?""",
                               (message.from_user.id,)).fetchone()
            if boss is not None:
                with open(f'./game/build_bus/{boss[0]}.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if not data['isbuilding']:
                        with open(f'./game/build_bus/{boss[0]}.json', 'w', encoding='utf-8') as f:
                            data['builders'].remove(message.from_user.id)
                            json.dump(data, f)
                            cur.execute("""DELETE FROM builders_work WHERE builder = ?""", (message.from_user.id,))
                            conn.commit()
                            await message.answer(
                                f'@{message.from_user.username}, вы ушли со стройки!')
                    else:
                        await message.answer(
                            f'@{message.from_user.username}, процесс стройки уже запущен, ожидайте окончания!')
            else:
                await message.answer(
                    f'@{message.from_user.username}, вы не работаете ни на каком строительном объекте!')
        else:
            await message.answer(f'@{message.from_user.username}, данная команда доступна только строителям!')
        cur.close()


def register_handlers_stroitel(dp: Dispatcher):
    dp.register_message_handler(build, commands='build')
    dp.register_message_handler(leave_build, commands='leave_build')
