from bot import InlineKeyboardButton, InlineKeyboardMarkup, database, res_database
from aiogram import types, Dispatcher, executor
from create_bot import dp, bot


@dp.message_handler(content_types='text', text=['Гараж', 'гараж'])
async def garage(message: types.Message):
    user_cars = list(database.users_cars.find({'id': message.from_user.id}))
    if user_cars != []:
        await message.delete()
        kb = InlineKeyboardMarkup(row_width=2)
        activate_btn = InlineKeyboardButton(text='Активировать',
                                            callback_data=f'activate_{str(message.from_user.id)}_{user_cars[0]["car"]}')
        next_page_btn = InlineKeyboardButton(text='▶', callback_data=f'next_page_{str(message.from_user.id)}_0')
        disactivate_btn = InlineKeyboardButton('Дизактивировать',
                                               callback_data=f'disactivate')
        kb.add(activate_btn, next_page_btn, disactivate_btn)
        await message.answer(text=f'Модель автомобиля: {user_cars[0]["car"]}\n'
                                  f'Расход топлива в час: {user_cars[0]["fuel_per_hour"]}\n'
                                  f'Сокращает время работы на: {user_cars[0]["save_job_time"]}%\n'
                                  f'Страница 1/{len(user_cars)}', reply_markup=kb, parse_mode='HTML')

    else:
        await message.reply(f"{message.from_user.first_name}, Вы пока нищий и у вас нет ни одной машины",
                            parse_mode='HTML')


@dp.callback_query_handler(lambda callback: 'activate_' in callback.data)
async def activate_car(callback: types.CallbackQuery):
    clbck = callback.data.replace('activate_', '').split('_')
    education_doc = database.education.find_one({'id': callback.from_user.id})
    if int(clbck[0]) == callback.from_user.id:
        if education_doc['auto_school'] == 'нет':
            await callback.message.answer(
                f'{callback.from_user.first_name} для того что-бы ездить на автомобиле вам нужно получить права',
                parse_mode='HTML')

        else:
            user_id = int(clbck[0])
            name_car = clbck[1]
            database.users_cars.update_one({'id': user_id, 'active': True}, {'$set': {'active': False}})
            database.users_cars.update_one({'id': user_id, 'car': name_car}, {'$set': {'active': True}})
            await callback.message.edit_text(f'Вы активировали автомобиль: {name_car}')
    else:
        await callback.answer('Это предназначено не вам!')

@dp.callback_query_handler(lambda callback: 'disactivate' in callback.data)
async def activate_car(callback: types.CallbackQuery):
    database.users_cars.update_one({'id': callback.from_user.id, 'active': True}, {'$set': {'active': False}})
    await callback.message.edit_text('Ваша машина дизактивирована!')
@dp.callback_query_handler(lambda callback: 'next_page_' in callback.data)
async def next_page_garage(callback: types.CallbackQuery):
    clbck = callback.data.replace('next_page_', '').split('_')
    page = int(clbck[1])
    user_id = int(clbck[0])
    if callback.from_user.id == user_id:
        user_cars = list(database.users_cars.find({'id': user_id}))
        if page + 2 != len(user_cars):
            page += 1
            user_cars = list(database.users_cars.find({'id': user_id}))
            kb = InlineKeyboardMarkup(row_width=1)
            activate_btn = InlineKeyboardButton(text='Активировать',
                                                callback_data=f'activate_{str(user_id)}_{user_cars[page]["car"]}')
            next_page_btn = InlineKeyboardButton(text='▶', callback_data=f'next_page_{str(user_id)}_{page}')
            previous_page_btn = InlineKeyboardButton(text='◀️',
                                                     callback_data=f'previous_page_{str(user_id)}_{page - 1}')
            kb.row(previous_page_btn, activate_btn, next_page_btn)
            await callback.message.edit_text(text=f'Модель автомобиля: {user_cars[page]["car"]}\n'
                                                  f'Расход топлива в час: {user_cars[page]["fuel_per_hour"]}\n'
                                                  f'Сокращает время работы на: {user_cars[page]["save_job_time"]}%\n'
                                                  f'Страница {page + 1}/{len(user_cars)}', reply_markup=kb,
                                             parse_mode='HTML')
            await callback.answer()
        elif page + 2 == len(user_cars):
            page += 1
            user_cars = list(database.users_cars.find({'id': user_id}))
            kb = InlineKeyboardMarkup(row_width=1)
            activate_btn = InlineKeyboardButton(text='Активировать',
                                                callback_data=f'activate_{str(user_id)}_{user_cars[page]["car"]}')
            previous_page_btn = InlineKeyboardButton(text='◀️',
                                                     callback_data=f'previous_page_{str(user_id)}_{page - 1}')
            kb.row(previous_page_btn, activate_btn)
            await callback.message.edit_text(text=f'Модель автомобиля: {user_cars[page]["car"]}\n'
                                                  f'Расход топлива в час: {user_cars[page]["fuel_per_hour"]}\n'
                                                  f'Сокращает время работы на: {user_cars[page]["save_job_time"]}%\n'
                                                  f'Страница {page + 1}/{len(user_cars)}', reply_markup=kb,
                                             parse_mode='HTML')
    else:
        await callback.answer('Это предназначено не вам')


@dp.callback_query_handler(lambda callback: 'previous_page_' in callback.data)
async def previous_page_garage(callback: types.CallbackQuery):
    clbck = callback.data.replace('previous_page_', '').split('_')
    page = int(clbck[1])
    user_id = int(clbck[0])
    if callback.from_user.id == user_id:
        if page != 0:
            page -= 1
            user_cars = list(database.users_cars.find({'id': user_id}))
            kb = InlineKeyboardMarkup(row_width=1)
            activate_btn = InlineKeyboardButton(text='Активировать',
                                                callback_data=f'activate_{str(user_id)}_{user_cars[page + 1]["car"]}')
            next_page_btn = InlineKeyboardButton(text='▶', callback_data=f'next_page_{str(user_id)}_{page}')
            previous_page_btn = InlineKeyboardButton(text='◀️', callback_data=f'previous_page_{str(user_id)}_{page}')
            kb.row(previous_page_btn, activate_btn, next_page_btn)
            await callback.message.edit_text(text=f'Модель автомобиля: {user_cars[page + 1]["car"]}\n'
                                                  f'Расход топлива в час: {user_cars[page + 1]["fuel_per_hour"]}\n'
                                                  f'Сокращает время работы на: {user_cars[page + 1]["save_job_time"]}%\n'
                                                  f'Страница {page + 2}/{len(user_cars)}', reply_markup=kb,
                                             parse_mode='HTML')
            await callback.answer()
        elif page == 0:

            user_cars = list(database.users_cars.find({'id': user_id}))
            kb = InlineKeyboardMarkup(row_width=1)
            activate_btn = InlineKeyboardButton(text='Активировать',
                                                callback_data=f'activate_{str(user_id)}_{user_cars[page + 1]["car"]}')
            next_page_btn = InlineKeyboardButton(text='▶', callback_data=f'next_page_{str(user_id)}_{page}')
            kb.row(activate_btn, next_page_btn)
            await callback.message.edit_text(text=f'Модель автомобиля: {user_cars[page]["car"]}\n'
                                                  f'Расход топлива в час: {user_cars[page]["fuel_per_hour"]}\n'
                                                  f'Сокращает время работы до: {user_cars[page]["save_job_time"]}\n'
                                                  f'Страница {page + 1}/{len(user_cars)}', reply_markup=kb,
                                             parse_mode='HTML')


    elif clbck != int(callback.from_user.id):
        await callback.answer('Это предназначено не вам')

    else:
        await callback.message.answer('Что то пошло не так')
