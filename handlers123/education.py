import asyncio
import json
import os

from bot import Dispatcher, check_user, database, types, InlineKeyboardButton, InlineKeyboardMarkup, \
    InputFile, quote_html, username, pytz, AsyncIOScheduler, username_2, res_database
import re
import datetime
import random
from create_bot import bot

# Пересдача цены
cost_retake = 500
exp_retake = 5

# Образование
async def education(message):
    await check_user(message)
    educ_info = database.education.find_one({'id': message.from_user.id})
    key = InlineKeyboardMarkup()
    school_but = InlineKeyboardButton('В школу', callback_data=f'go_school')
    # Если еще не учился
    if educ_info is None:
        database.education.insert_one({'id': message.from_user.id,
                                       'ucheb': 'нет',
                                       'class': 'нет',
                                       'jobs': 'Раб Дворник Дояр',
                                       'status': 'нет',
                                       'right': 0,
                                       'wrong': 0,
                                       'school': 'нет',
                                       'auto_school': 'нет',
                                       'retake': False,
                                       'error': 0})

        iq = 100
        with open(f'{os.getcwd()}/res/iq.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            f.close()
            for line in lines:
                nums = line.split('.')[1]
                num1, num2 = nums.split('-')
                if round(iq) in range(int(num1), int(num2) + 1):
                    msg_iq = line.split('.')[0].lower()
                    break
        key.add(school_but)
        await bot.send_message(message.chat.id, f'🎓 {await username(message)} ваше образование: 🎓\n'
                                                f'🧠 IQ как у {msg_iq}\n'
                                                f'🏫 Учебное заведение: нет\n'
                                                f'🪪 Права B категории: нет\n\n'
                                                '💼 Доступные работы: 💼\n'
                                                f'Раб, Дворник, Дояр\n', reply_markup=key, parse_mode='HTML')
    # Если вызывал учебу
    elif educ_info['ucheb'] == 'Школа':

        msg_class = '🎗 Класс: ' + f'{educ_info["class"]}\n' if educ_info['status'] == 'учусь' else ''
        msg_iq = None
        try:
            iq = educ_info['right'] / educ_info['wrong']
            with open(f'{os.getcwd()}/res/iq.txt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                f.close()
                for line in lines:
                    nums = line.split('.')[1]
                    num1, num2 = nums.split('-')
                    if round(iq) in range(int(num1), int(num2) + 1):
                        msg_iq = line.split('.')[0].lower()
                        break
        except:
            iq = 100
            with open(f'{os.getcwd()}/res/iq.txt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                f.close()
                for line in lines:
                    nums = line.split('.')[1]
                    num1, num2 = nums.split('-')

                    if round(iq) in range(int(num1), int(num2) + 1):
                        msg_iq = line.split('.')[0].lower()
                        break
        if educ_info['school'] == 'нет' or educ_info is None:
            key.add(school_but)
        elif educ_info['school'] == 'да':
            key.add(InlineKeyboardButton('Продолжить обучение', callback_data='retake'))
        jobs = re.split(r"\s+(?=[А-Я])", educ_info["jobs"])
        await bot.send_message(message.chat.id, f'🎓 {await username(message)} ваше образование: 🎓\n'
                                                f'🧠 IQ как у {msg_iq}\n'
                                                f'🏫 Учебное заведение: {educ_info["ucheb"]}\n'
                                                f'{msg_class if educ_info["status"] == "учусь" else ""}'
                                                f'🪪 Права B категории: {educ_info["auto_school"]}\n\n'
                                                '💼 Доступные работы: 💼\n'
                                                f'{", ".join(jobs)}\n', reply_markup=key,
                               parse_mode='HTML')
    else:
        msg_iq = None
        try:
            iq = educ_info['right'] / educ_info['wrong']
            with open(f'{os.getcwd()}/res/iq.txt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                f.close()
                for line in lines:
                    nums = line.split('.')[1]
                    num1, num2 = nums.split('-')
                    if round(iq) in range(int(num1), int(num2) + 1):
                        msg_iq = line.split('.')[0].lower()
                        break
        except:
            iq = 100
            with open(f'{os.getcwd()}/res/iq.txt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                f.close()
                for line in lines:
                    nums = line.split('.')[1]
                    num1, num2 = nums.split('-')
                    if round(iq) in range(int(num1), int(num2) + 1):
                        msg_iq = line.split('.')[0].lower()
                        break
        key = InlineKeyboardMarkup()
        if educ_info['status'] == 'учусь':
            key.add(InlineKeyboardButton('Продолжить обучение', callback_data='start_teor'))
        elif educ_info['status'] == 'нет':
            key.add(school_but)
        elif educ_info['status'] == 'окончил':
            key.add(InlineKeyboardButton('ВУЗы', callback_data=f'go_school'))
        jobs = re.split(r"\s+(?=[А-Я])", educ_info["jobs"])
        await bot.send_message(message.chat.id, f'🎓 {await username(message)} ваше образование: 🎓\n'
                                                f'🧠 IQ как у {msg_iq}\n'
                                                f'🏫 Учебное заведение: {educ_info["ucheb"]}\n'
                                                f'🪪 Права B категории: {educ_info["auto_school"]}\n\n'
                                                '💼 Доступные работы: 💼\n'
                                                f'{", ".join(jobs)}\n',
                               parse_mode='HTML', reply_markup=key)

# Учеба
async def ucheba(message):
    await check_user(message)
    # Если учится в вузе
    vuz_info = res_database.vuz.find_one({'id': message.from_user.id})
    if vuz_info is not None:
        # Получение переменных с строки
        tz = pytz.timezone('Etc/GMT-3')
        date, time = vuz_info['time'].split(' ')
        year, month, day = date.split('-')
        hour, minute, second = time.split(':')
        time_vuz = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
        time_now = datetime.datetime(datetime.datetime.now(tz=tz).year, datetime.datetime.now(tz=tz).month,
                                     datetime.datetime.now(tz=tz).day, datetime.datetime.now(tz=tz).hour,
                                     datetime.datetime.now(tz=tz).minute, datetime.datetime.now(tz=tz).second)
        result = time_vuz - time_now
        if '-' not in str(result):
            await bot.send_message(message.chat.id, f'{await username(message)}, вам ещё осталось учиться {result} на {vuz_info["job"]}', parse_mode='HTML')
            return

    if message.chat.type == 'private':
        educ_info = database.education.find_one({'id': message.from_user.id})
        if educ_info is not None:
            # Если окончил 11 класс
            if educ_info['status'] == 'окончил':
                # Работы, которые еще не получил
                jobs_list = []
                jobs_info = database.jobs.find()
                for job in list(jobs_info):
                    jobs_list.append(job['name_job'])
                for job in re.split(r"\s+(?=[А-Я])", educ_info['jobs']):
                    if job in jobs_list:
                        jobs_list.remove(job)
                key = InlineKeyboardMarkup()
                for job in jobs_list:
                    key.add(InlineKeyboardButton(job, callback_data=f'vuz_{job}'))
                await bot.send_message(message.chat.id, f'{await username(message)}, вам доступны следующие ВУЗы:', reply_markup=key,parse_mode='HTML')
                return
            arr = next(os.walk(f'{os.getcwd()}/res/education/{educ_info["class"]}/teor'))[2]
            all_teor = []
            for item in arr:
                all_teor.append(int(item.replace('.txt', '')))
            # Если еще есть теория
            if max(all_teor) >= educ_info['num_teoria']:
                key = InlineKeyboardMarkup()
                # Если вводынй файл то прсото читаем
                if educ_info['num_teoria'] == 0:
                    # обновление данных в БД
                    database.education.update_one({'id': message.from_user.id},
                                                  {'$set': {'num_teoria': educ_info['num_teoria'] + 1}})
                    with open(
                            f'{os.getcwd()}/res/education/{educ_info["class"]}/teor/{educ_info["num_teoria"]}.txt',
                            'r',
                            encoding='utf-8') as f:
                        file = f.readlines()
                        f.close()
                    but1 = InlineKeyboardButton('Начать', callback_data='start_teor')
                    key.add(but1)
                    await bot.send_message(message.chat.id, ''.join(file), reply_markup=key)

                else:
                    msg_data = [f'#Теория {educ_info["num_teoria"]}/{max(all_teor)}\n\n']
                    with open(
                            f'{os.getcwd()}/res/education/{educ_info["class"]}/teor/{educ_info["num_teoria"]}.txt',
                            'r',
                            encoding='utf-8') as f:
                        file = f.readlines()
                        f.close()
                        for line in file:
                            msg_data.append('    ' + line)
                        but1 = InlineKeyboardButton('Далее', callback_data='start_teor')
                        key.add(but1)
                        await bot.send_message(message.chat.id, ''.join(msg_data), reply_markup=key)

            else:
                arr = next(os.walk(f'{os.getcwd()}/res/education/{educ_info["class"]}/prac'))[2]
                all_prac = []
                for item in arr:
                    all_prac.append(int(item.replace('.txt', '')))
                # Если это первый вводный файл
                if educ_info['num_question'] == 0:
                    with open(
                            f'{os.getcwd()}/res/education/{educ_info["class"]}/prac/{educ_info["num_question"]}.txt',
                            'r',
                            encoding='utf-8') as f:
                        f.close()
                        key = InlineKeyboardMarkup()
                        but1 = InlineKeyboardButton('Далее', callback_data='start_teor')
                        key.add(but1)
                        await bot.send_message(message.chat.id,
                                               'Вы получили некоторые теоритические знания, теперь приступим к тесту\n'
                                               '    - Первая сдача БЕСПЛАТНО\n'
                                               '    - Каждая следующая:\n'
                                               f'              - {cost_retake}$\n'
                                               f'              - {exp_retake} опыта\n'
                                               '   * 3 ошибки - не сдал', reply_markup=key)
                # Если тестовые задания
                else:
                    if max(all_prac) >= educ_info['num_question']:
                        if educ_info['retake']:
                            key = InlineKeyboardMarkup()
                            but_yes = InlineKeyboardButton('Да', callback_data='retake_yes')
                            but_no = InlineKeyboardButton('Нет', callback_data='retake_no')
                            key.add(but_yes, but_no)
                            await bot.send_message(message.chat.id, 'Стоимость сдачи теста повторно:\n'
                                                                    f'    - {cost_retake}$\n'
                                                                    f'    - {exp_retake} опыта\n\n'
                                                                    f'Хотите пересдать тест?', reply_markup=key)
                        else:
                            await start_teor(message)
                    else:
                        # Смена класса
                        await bot.send_message(message.chat.id, 'Вы успешно прошли обучение!')
        else:
            await bot.send_message(message.chat.id, 'Чтобы начать обучение введи /education')
    else:
        await bot.send_message(message.chat.id,f'{await username(message)}, доступно только в личном чате с ботом!', parse_mode='HTML')


# Пересдача
async def retake(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    educ_info = database.education.find_one({'id': user_id})
    if educ_info['retake']:
        key = InlineKeyboardMarkup()
        but_yes = InlineKeyboardButton('Да', callback_data='retake_yes')
        but_no = InlineKeyboardButton('Нет', callback_data='retake_no')
        key.add(but_yes, but_no)
        await bot.send_message(callback.message.chat.id, 'Стоимость сдачи теста повторно:\n'
                                                         f'    - {cost_retake}$\n'
                                                         f'    - {exp_retake} опыта\n\n'
                                                         f'Хотите пересдать тест?', reply_markup=key)
    else:
        await start_teor(callback)


# Пересдать ДА
async def retake_yes(callback: types.CallbackQuery):
    user_info = database.users.find_one({'id': callback.from_user.id})
    if user_info['cash'] >= cost_retake and user_info['exp'] >= exp_retake:
        # Обновление БД
        database.users.update_one({'id': callback.from_user.id}, {'$set': {'cash': user_info['cash'] - cost_retake,
                                                                           'exp': user_info['exp'] - exp_retake,
                                                                           'retake': False}})
        await start_teor(callback)
    else:
        await callback.message.edit_text(f'{await username(callback)},у вас недостаточно средств!',
                                         parse_mode='HTML')


# Пересдать НЕТ
async def retake_no(callback: types.CallbackQuery):
    await callback.message.delete()


# В школу кнопка
async def go_school(callback: types.CallbackQuery):
    await check_user(callback)
    user_id = callback.from_user.id
    educ_info = database.education.find_one({'id': user_id})
    key = InlineKeyboardMarkup()
    if educ_info['status'] == 'учусь':
        await callback.answer('Вы уже учитесь!')
    elif educ_info['status'] == 'окончил':
        # Работы, которые еще не получил
        jobs_list = []
        jobs_info = database.jobs.find()
        for job in list(jobs_info):
            jobs_list.append(job['name_job'])
        for job in re.split(r"\s+(?=[А-Я])", educ_info['jobs']):
            if job in jobs_list:
                jobs_list.remove(job)
        key = InlineKeyboardMarkup()
        for job in jobs_list:
            key.add(InlineKeyboardButton(job, callback_data=f'vuz_{job}'))
        await callback.message.edit_text('Вам доступны следующие ВУЗы:', reply_markup=key)
    elif educ_info['status'] == 'нет':
        but_yes = InlineKeyboardButton('Да', callback_data=f'school_yes_{user_id}')
        but_no = InlineKeyboardButton('Нет', callback_data=f'school_no_{user_id}')
        key.add(but_yes, but_no)
        await callback.message.edit_text('Стоимость обучения:\n'
                                         '   - 3000$\n'
                                         '   - 60 опыта\n'
                                         'Вы действительно хотите начать обучение в школе?', reply_markup=key)


# Старт теория
async def start_teor(callback: types.CallbackQuery):
    await check_user(callback)
    user_id = callback.from_user.id

    educ_info = database.education.find_one({'id': user_id})
    if educ_info['status'] == 'окончил':
        await callback.message.edit_text(f'{await username(callback)}, вы уже окончили школу!\n'
                                         'Вам доступны ВУЗы - напишите "вуз"', parse_mode='HTML')
        return
    arr = next(os.walk(f'{os.getcwd()}/res/education/{educ_info["class"]}/teor'))[2]
    all_teor = []
    for item in arr:
        all_teor.append(int(item.replace('.txt', '')))
    # Если еще есть теория
    if max(all_teor) >= educ_info['num_teoria']:
        msg_data = [f'#Теория {educ_info["num_teoria"]}/{max(all_teor)}\n\n']
        with open(f'{os.getcwd()}/res/education/{educ_info["class"]}/teor/{educ_info["num_teoria"]}.txt', 'r',
                  encoding='utf-8') as f:
            file = f.readlines()
            f.close()
            for line in file:
                msg_data.append('    ' + line)
        key = InlineKeyboardMarkup()
        but1 = InlineKeyboardButton('Далее', callback_data='next_teor')
        key.add(but1)
        if callback.message.chat.type == 'private':
            await callback.message.edit_text(''.join(msg_data), reply_markup=key)
        else:
            await callback.message.delete()
            await bot.send_message(callback.from_user.id, ''.join(msg_data), reply_markup=key)
    # Если практика
    else:
        arr = next(os.walk(f'{os.getcwd()}/res/education/{educ_info["class"]}/prac'))[2]
        all_prac = []
        for item in arr:
            all_prac.append(int(item.replace('.txt', '')))
        # Если это первый вводный файл
        if educ_info['num_question'] == 0:
            # обновление данных в БД
            database.education.update_one({'id': user_id},
                                          {'$set': {'num_question': educ_info['num_question'] + 1}})
            with open(f'{os.getcwd()}/res/education/{educ_info["class"]}/prac/{educ_info["num_question"]}.txt', 'r',
                      encoding='utf-8') as f:
                file = f.readlines()
                f.close()
                key = InlineKeyboardMarkup()
                but1 = InlineKeyboardButton('Далее', callback_data='next_prac')
                key.add(but1)
                if callback.message.chat.type == 'private':
                    await callback.message.edit_text(
                        'Вы получили некоторые теоритические знания, теперь приступим к тесту\n'
                        '    - Первая сдача БЕСПЛАТНО\n'
                        '    - Каждая следующая:\n'
                        f'              - {cost_retake}$\n'
                        f'              - {exp_retake} опыта\n'
                        '   * 3 ошибки - не сдал', reply_markup=key)
                else:
                    await callback.message.delete()
                    await bot.send_message(callback.from_user.id,
                                           'Вы получили некоторые теоритические знания, теперь приступим к тесту\n'
                                           '    - Первая сдача БЕСПЛАТНО\n'
                                           '    - Каждая следующая:\n'
                                           f'              - {cost_retake}$\n'
                                           f'              - {exp_retake} опыта\n'
                                           '   * 3 ошибки - не сдал', reply_markup=key)
        # Если вопрос
        elif max(all_prac) >= educ_info['num_question']:
            msg_data = [f'#Практика {educ_info["num_question"]}/{max(all_prac)}\n\n']
            with open(f'{os.getcwd()}/res/education/{educ_info["class"]}/prac/{educ_info["num_question"]}.txt', 'r',
                      encoding='utf-8') as f:
                file = f.readlines()
                f.close()

                question, correct, wrong = str(random.choice(file)).split(':')
                # Список с ответами
                answers = [word for word in wrong.split('.')]
                answers.append(correct)
                msg_data.append('Вопрос:\n' + question)
                key = InlineKeyboardMarkup(1)
                for i in range(0, len(answers)):
                    answer = random.choice(answers)
                    answers.remove(answer)
                    if answer == correct:
                        but_ans = InlineKeyboardButton(answer, callback_data=f'ans_correct')
                    else:
                        but_ans = InlineKeyboardButton(answer, callback_data=f'ans_wrong{random.randint(1, 6)}')
                    key.insert(but_ans)
                msg_data.append(f'\n\n    - Ошибок: {educ_info["error"]}/3')
                try:
                    if callback.message.chat.type == 'private':
                        await callback.message.edit_text(''.join(msg_data), reply_markup=key)
                    else:
                        await callback.message.delete()
                        await bot.send_message(callback.from_user.id,
                                               ''.join(msg_data), reply_markup=key)
                except:
                    await bot.send_message(callback.chat.id, ''.join(msg_data), reply_markup=key)
        else:
            await bot.send_message(callback.message.chat.id,
                                   f'{await username(callback)}, вы полностью прошли обучение!', parse_mode='HTML')


# Ответ правильный
async def ans_correct(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    # Обновление БД
    educ_info = database.education.find_one({'id': user_id})
    database.education.update_one({'id': user_id}, {'$set': {'num_question': educ_info['num_question'] + 1,
                                                             'right': educ_info['right'] + 1}})
    educ_info = database.education.find_one({'id': user_id})
    # Кол-во практики
    arr = next(os.walk(f'{os.getcwd()}/res/education/{educ_info["class"]}/prac'))[2]
    all_prac = []
    for item in arr:
        all_prac.append(int(item.replace('.txt', '')))
    # Если тест закончился
    if educ_info['num_question'] > max(all_prac):
        # Если был 11 класс, то учебу окончил
        if int(educ_info["class"].split(" ")[0]) + 1 == 12:
            await callback.message.edit_text('Поздравляю, вы окончили школу!\n'
                                             'Теперь вам доступны большие возможности!')
            database.education.update_one({'id': callback.from_user.id}, {'$set': {'status': 'окончил',
                                                                                   'ucheb': 'нет'}})
        else:
            key = InlineKeyboardMarkup()
            # обновление данных в БД
            database.education.update_one({'id': callback.from_user.id},
                                          {'$set': {'num_teoria': 1,
                                                    'class': f'{int(educ_info["class"].split(" ")[0]) + 1} класс',
                                                    'error': 0,
                                                    'num_question': 0}})
            educ_info = database.education.find_one({'id': user_id})
            with open(
                    f'{os.getcwd()}/res/education/{educ_info["class"]}/teor/0.txt',
                    'r',
                    encoding='utf-8') as f:
                file = f.readlines()
                f.close()
            but1 = InlineKeyboardButton('Начать', callback_data='start_teor')
            key.add(but1)
            await callback.message.edit_text(''.join(file), reply_markup=key)
    else:
        msg_data = [f'#Практика {educ_info["num_question"]}/{max(all_prac)}\n\n']
        with open(f'{os.getcwd()}/res/education/{educ_info["class"]}/prac/{educ_info["num_question"]}.txt', 'r',
                  encoding='utf-8') as f:
            file = f.readlines()
            f.close()

            question, correct, wrong = str(random.choice(file)).split(':')
            # Список с ответами
            answers = [word for word in wrong.split('.')]
            answers.append(correct)
            msg_data.append('Вопрос:\n' + question)
            key = InlineKeyboardMarkup(1)
            for i in range(0, len(answers)):
                answer = random.choice(answers)
                answers.remove(answer)
                if answer == correct:
                    but_ans = InlineKeyboardButton(answer, callback_data=f'ans_correct')
                else:
                    but_ans = InlineKeyboardButton(answer, callback_data=f'ans_wrong{random.randint(1, 6)}')
                key.insert(but_ans)
            msg_data.append(f'\n\n    - Ошибок: {educ_info["error"]}/3')
            await callback.message.edit_text(''.join(msg_data), reply_markup=key)
    await bot.answer_callback_query(callback.id)


# Ответ неправильный
async def ans_wrong(callback):
    user_id = callback.from_user.id
    # Обновление БД
    educ_info = database.education.find_one({'id': user_id})
    database.education.update_one({'id': user_id}, {'$set': {'num_question': educ_info['num_question'] + 1,
                                                             'error': educ_info['error'] + 1,
                                                             'wrong': educ_info['wrong'] + 1}})
    educ_info = database.education.find_one({'id': user_id})
    if educ_info['error'] >= 3:
        key = InlineKeyboardMarkup()
        key.add(InlineKeyboardButton('Пересдать тест', callback_data='retake'))
        await callback.message.edit_text('Вы ошиблись 3 раза!', reply_markup=key)
        database.education.update_one({'id': user_id}, {'$set': {'retake': True,
                                                                 'error': 0,
                                                                 'num_question': 1}})
        return
    # Кол-во практики
    arr = next(os.walk(f'{os.getcwd()}/res/education/{educ_info["class"]}/prac'))[2]
    all_prac = []
    for item in arr:
        all_prac.append(int(item.replace('.txt', '')))
    # Если тест закончился
    if educ_info['num_question'] > max(all_prac):
        msg_data = [f'#Практика {max(all_prac)}/{max(all_prac)}\n\n']
        with open(f'{os.getcwd()}/res/education/{educ_info["class"]}/prac/{max(all_prac)}.txt', 'r',
                  encoding='utf-8') as f:
            file = f.readlines()
            f.close()

            question, correct, wrong = str(random.choice(file)).split(':')
            # Список с ответами
            answers = [word for word in wrong.split('.')]
            answers.append(correct)
            msg_data.append('Вопрос:\n' + question)
            key = InlineKeyboardMarkup(1)

            for i in range(0, len(answers)):
                answer = random.choice(answers)
                answers.remove(answer)
                if answer == correct:
                    but_ans = InlineKeyboardButton(answer, callback_data=f'ans_correct')
                else:
                    but_ans = InlineKeyboardButton(answer, callback_data=f'ans_wrong{random.randint(1,6)}')
                key.insert(but_ans)
            msg_data.append(f'\n\n    - Ошибок: {educ_info["error"]}/3')
            await callback.message.edit_text(''.join(msg_data), reply_markup=key)
    else:
        msg_data = [f'#Практика {educ_info["num_question"]}/{max(all_prac)}\n\n']
        with open(f'{os.getcwd()}/res/education/{educ_info["class"]}/prac/{educ_info["num_question"]}.txt', 'r',
                  encoding='utf-8') as f:
            file = f.readlines()
            f.close()

            question, correct, wrong = str(random.choice(file)).split(':')
            # Список с ответами
            answers = [word for word in wrong.split('.')]
            answers.append(correct)
            msg_data.append('Вопрос:\n' + question)
            key = InlineKeyboardMarkup(1)
            for i in range(0, len(answers)):
                answer = random.choice(answers)
                answers.remove(answer)
                if answer == correct:
                    but_ans = InlineKeyboardButton(answer, callback_data=f'ans_correct')
                else:
                    but_ans = InlineKeyboardButton(answer, callback_data=f'ans_wrong{random.randint(1,6)}')
                key.insert(but_ans)
            msg_data.append(f'\n\n    - Ошибок: {educ_info["error"]}/3')
            await callback.message.edit_text(''.join(msg_data), reply_markup=key)
    await bot.answer_callback_query(callback.id)


# След теория
async def next_teor(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    # обновление данных в БД
    educ_info = database.education.find_one({'id': user_id})
    database.education.update_one({'id': user_id},
                                  {'$set': {'num_teoria': educ_info['num_teoria'] + 1}})
    await start_teor(callback)


# След практика
async def next_prac(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    # обновление данных в БД
    educ_info = database.education.find_one({'id': user_id})
    if educ_info['num_question'] == 0:
        database.education.update_one({'id': user_id},
                                      {'$set': {'num_question': educ_info['num_question'] + 1}})
    await start_teor(callback)



# ВУЗ
async def vuz(message: types.Message):
    await check_user(message)
    # Если учится в вузе
    vuz_info = res_database.vuz.find_one({'id': message.from_user.id})
    if vuz_info is not None:
        # Получение переменных с строки
        tz = pytz.timezone('Etc/GMT-3')
        date, time = vuz_info['time'].split(' ')
        year, month, day = date.split('-')
        hour, minute, second = time.split(':')
        time_vuz = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
        time_now = datetime.datetime(datetime.datetime.now(tz=tz).year, datetime.datetime.now(tz=tz).month,
                                     datetime.datetime.now(tz=tz).day, datetime.datetime.now(tz=tz).hour,
                                     datetime.datetime.now(tz=tz).minute, datetime.datetime.now(tz=tz).second)
        result = time_vuz - time_now
        if '-' not in str(result):
            await bot.send_message(message.chat.id,
                                   f'{await username(message)}, вам ещё осталось учиться {result} на {vuz_info["job"]}',
                                   parse_mode='HTML')
            return
    educ_info = database.education.find_one({'id': message.from_user.id})

    # Если не окончил
    if educ_info['status'] != 'окончил':
        await bot.send_message(message.chat.id, f'{await username(message)}, для начала вам нужно окончить школу!',
                               reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton('Начать',
                                                                                            callback_data='go_school')), parse_mode='HTML')
    # Если окончил
    else:
        # Работы, которые еще не получил
        jobs_list = []
        jobs_info = database.jobs.find()
        for job in list(jobs_info):
            jobs_list.append(job['name_job'])
        for job in re.split(r"\s+(?=[А-Я])", educ_info['jobs']):
            if job in jobs_list:
                jobs_list.remove(job)
        key = InlineKeyboardMarkup()
        for job in jobs_list:
            key.add(InlineKeyboardButton(job, callback_data=f'vuz_{job}'))
        await bot.send_message(message.chat.id, f'{await username(message)}, вам доступны следующие ВУЗы:', reply_markup=key, parse_mode='HTML')





def register_handler_education(dp: Dispatcher):
    dp.register_callback_query_handler(start_teor, text='start_teor')
    dp.register_callback_query_handler(go_school, text='go_school')
    dp.register_callback_query_handler(next_teor, text='next_teor')
    dp.register_callback_query_handler(next_prac, text='next_prac')
    dp.register_message_handler(ucheba, content_types='text', text=['Учеба', 'учеба', 'УЧЕБА'])
    dp.register_callback_query_handler(ans_correct, text='ans_correct')
    dp.register_callback_query_handler(ans_wrong, text=['ans_wrong1', 'ans_wrong2', 'ans_wrong3', 'ans_wrong4', 'ans_wrong5', 'ans_wrong6'])
    dp.register_callback_query_handler(retake_yes, text='retake_yes')
    dp.register_callback_query_handler(retake_no, text='retake_no')
    dp.register_callback_query_handler(retake, text='retake')
    dp.register_message_handler(vuz, content_types='text', text=['ВУЗ', 'вуз', 'Вуз', 'ВУЗЫ', 'Вузы', 'вузы'])
    dp.register_message_handler(education, commands='education')
