from bot import check_user, types, username, Dispatcher, database, res_database, bot


# /heal Лечение (доступно только фельдшеру)
async def heal(message: types.Message):
    user_id = message.from_user.id
    await check_user(message)
    user_info = database.users.find_one({'id': user_id})
    if user_info['job'] == 'Фельдшер':  # Если врач
        if message.from_user.id == message.reply_to_message.from_user.id:
            await message.answer(f'{await username(message)}, вы не можете лечить сами себя!', parse_mode='HTML')
            return
        if message.reply_to_message:
            id_user_reply = message.reply_to_message.from_user.id
            disease_info = res_database.disease.find_one({'id': id_user_reply})

            if disease_info is not None and disease_info['disease']:  # Если болеет
                money = message.get_args().split()
                if '-' in money[0]:
                    await message.answer(f'{await username(message)}, введите корректную сумму', parse_mode='HTML')
                    return
                try:
                    cash = int(money[0])
                    user_reply_info = database.users.find_one({'id': id_user_reply})
                    if user_reply_info['cash'] >= cash:
                        key = types.InlineKeyboardMarkup()
                        but_yes = types.InlineKeyboardButton(text='Согласиться', callback_data=f'Фельдшер_да.{message.from_user.id}.{message.reply_to_message.from_user.id}.{cash}')
                        but_no = types.InlineKeyboardButton(text='Отказаться', callback_data=f'Фельдшер_нет.{message.from_user.id}.{message.reply_to_message.from_user.id}.{cash}')
                        key.add(but_no, but_yes)
                        await bot.send_message(message.chat.id, f'{await username(message.reply_to_message)},'
                                                                f' вас хочет вылечить {await username(message)} за {cash}$',
                                               reply_markup=key, parse_mode='HTML')
                    else:
                        await message.answer(
                            f'{await username(message.reply_to_message)}, не имеет столько средств',parse_mode='HTML')
                except:
                    await message.answer(f'{await username(message)}, сумма ведена некорректно',parse_mode='HTML')
            else:
                await message.answer(f'{await username(message.reply_to_message)}, ничем не болеет',parse_mode='HTML')
        else:
            await message.answer(
                'Чтобы вылечить нужно ответит на сообщение больного командой "/heal сумма"')
    else:
        await message.answer(f'{await username(message)}, вы не являетесь фельдшером',parse_mode='HTML')


def register_handlers_feldsher(dp: Dispatcher):
    dp.register_message_handler(heal, commands='heal')