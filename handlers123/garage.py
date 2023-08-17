from bot import InlineKeyboardButton, InlineKeyboardMarkup, database, res_database
from aiogram import types, Dispatcher, executor
from create_bot import dp, bot

@dp.message_handler(content_types='text', text=['Гараж', 'гараж'])
async def garage(message: types.Message):
    user_cars = list(database.users_cars.find({'id': message.from_user.id}))
    if user_cars != None:
        await message.delete()
        kb = InlineKeyboardMarkup(row_width=1)
        activate_btn = InlineKeyboardButton(text='Активировать', callback_data=f'activate_{str(message.from_user.id)}_{user_cars[0]["car"]}')
        next_page_btn = InlineKeyboardButton(text='▶', callback_data=f'next_page_{str(message.from_user.id)}_0')
        kb.row(activate_btn, next_page_btn)
        await message.answer(text=f'Модель автомобиля: {user_cars[0]["car"]}\n'
                                                  f'Расход топлива в час: {user_cars[0]["fuel_per_hour"]}\n'
                                                  f'Сокращает время работы до: {user_cars[0]["save_job_time"]}\n'
                                                  f'Страница 1/{len(user_cars)}', reply_markup=kb, parse_mode='HTML')

    elif user_cars == None:
        await message.reply(f"{message.from_user.first_name}, Вы пока нищий и у вас нет ни одной машины", parse_mode='HTML')


@dp.callback_query_handler(lambda callback: 'activate_' in callback.data)
async def activate_car(callback: types.CallbackQuery):
    clbck = callback.data.replace('activate_', '').split('_')
    print(clbck)
    education_doc = database.education.find_one({'id': callback.from_user.id})
    if int(clbck[0]) == callback.from_user.id:
        if education_doc['auto_school'] == 'нет':
            await callback.message.answer(f'{callback.from_user.first_name} для того что-бы ездить на автомобиле вам нужно получить права', parse_mode='HTML')
            await callback.answer()
    else:
        await callback.answer('Это предназначено не вам!')