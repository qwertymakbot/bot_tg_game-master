from bot import *

msg_data = [f'Поздравляем нашего президента!!! 🧔\n'
            f'🛠 Вам доступны следующие команды:\n'
            f'/get_citizen, Взять гражданина - делаете участника гражданином своей страны (нужно ответить командой на сообщение участника)\n'
            f'/nalog 1 - устанавливает налог на работу в размере 1% (цифра может быть любая от 0 до 100)\n'
            f'/mycitizens, Граждане, Мои граждане - покажет список ваших гражданов\n'
            f'/ccash - управление деньгами в казне\n'
            f'/cpass, О стране, Моя страна - данные о вашей стране\n'
            f'/sell_country, Продать страну - продажа страны']


# Хендлеры
async def country_armenia(callback: types.CallbackQuery):
    await check_user(callback)
    user_id = callback.from_user.id
    country = callback.data
    with sqlite3.connect('game/data.db', timeout=10) as conn:
        cur = conn.cursor()
        president, cash = cur.execute("""SELECT president_country, cash FROM users WHERE user_id = ?""",
                                      (user_id,)).fetchone()
        cost, country_presedent = cur.execute("""SELECT cost, president FROM countries WHERE country = ?""",
                                              (country,)).fetchone()
        if president == 'нет' and cash >= cost and country_presedent == 0:
            # Вычет денег из баланса
            cur.execute("""UPDATE users SET cash = ?, president_country = ?, citizen_country = ? WHERE user_id = ?""",
                        (cash - cost, country, country, user_id))
            conn.commit()
            # Страна обрела президента
            cur.execute("""UPDATE countries SET president = ? WHERE country = ?""", (user_id, country))
            conn.commit()
            await bot.send_message(callback.message.chat.id,
                                   text=f'@{callback.from_user.username} успешно купил страну - {country}! 🌍\n' + ''.join(
                                       msg_data))
        elif cash < cost:
            await callback.answer(f'Ваш нужно ещё {cost - cash:n}$')
        elif president != 'нет':
            pres_count = cur.execute("""SELECT president_country FROM users WHERE user_id = ?""", (user_id,)).fetchone()
            await callback.answer(f'Вы уже президент страны {pres_count[0]}')
        elif country_presedent != 0:
            id_user = cur.execute("""SELECT president FROM countries WHERE country = ?""", (country,)).fetchone()
            idname = await bot.get_chat(id_user[0])
            named = quote_html(idname.username)
            await callback.answer(f'У страны {country} уже есть президент {named}')
        cur.close()


async def country_belarus(callback: types.CallbackQuery):
    await check_user(callback)
    user_id = callback.from_user.id
    country = callback.data
    with sqlite3.connect('game/data.db', timeout=10) as conn:
        cur = conn.cursor()
        president, cash = cur.execute("""SELECT president_country, cash FROM users WHERE user_id = ?""",
                                      (user_id,)).fetchone()
        cost, country_presedent = cur.execute("""SELECT cost, president FROM countries WHERE country = ?""",
                                              (country,)).fetchone()
        if president == 'нет' and cash >= cost and country_presedent == 0:
            # Вычет денег из баланса
            cur.execute("""UPDATE users SET cash = ?, president_country = ?, citizen_country = ? WHERE user_id = ?""",
                        (cash - cost, country, country, user_id))
            conn.commit()
            # Страна обрела президента
            cur.execute("""UPDATE countries SET president = ? WHERE country = ?""", (user_id, country))
            conn.commit()
            await bot.send_message(callback.message.chat.id,
                                   text=f'@{callback.from_user.username} успешно купил страну - {country}! 🌍\n' + ''.join(
                                       msg_data))
        elif cash < cost:
            await callback.answer(f'Ваш нужно ещё {cost - cash:n}$')
        elif president != 'нет':
            pres_count = cur.execute("""SELECT president_country FROM users WHERE user_id = ?""", (user_id,)).fetchone()
            await callback.answer(f'Вы уже президент страны {pres_count[0]}')
        elif country_presedent != 0:
            id_user = cur.execute("""SELECT president FROM countries WHERE country = ?""", (country,)).fetchone()
            idname = await bot.get_chat(id_user[0])
            named = quote_html(idname.username)
            await callback.answer(f'У страны {country} уже есть президент {named}')
        cur.close()

async def country_brazilia(callback: types.CallbackQuery):
    await check_user(callback)
    user_id = callback.from_user.id
    country = callback.data
    with sqlite3.connect('game/data.db', timeout=10) as conn:
        cur = conn.cursor()
        president, cash = cur.execute("""SELECT president_country, cash FROM users WHERE user_id = ?""",
                                      (user_id,)).fetchone()
        cost, country_presedent = cur.execute("""SELECT cost, president FROM countries WHERE country = ?""",
                                              (country,)).fetchone()
        if president == 'нет' and cash >= cost and country_presedent == 0:
            # Вычет денег из баланса
            cur.execute("""UPDATE users SET cash = ?, president_country = ?, citizen_country = ? WHERE user_id = ?""",
                        (cash - cost, country, country, user_id))
            conn.commit()
            # Страна обрела президента
            cur.execute("""UPDATE countries SET president = ? WHERE country = ?""", (user_id, country))
            conn.commit()
            await bot.send_message(callback.message.chat.id,
                                   text=f'@{callback.from_user.username} успешно купил страну - {country}! 🌍\n' + ''.join(
                                       msg_data))
        elif cash < cost:
            await callback.answer(f'Ваш нужно ещё {cost - cash:n}$')
        elif president != 'нет':
            pres_count = cur.execute("""SELECT president_country FROM users WHERE user_id = ?""", (user_id,)).fetchone()
            await callback.answer(f'Вы уже президент страны {pres_count[0]}')
        elif country_presedent != 0:
            id_user = cur.execute("""SELECT president FROM countries WHERE country = ?""", (country,)).fetchone()
            idname = await bot.get_chat(id_user[0])
            named = quote_html(idname.username)
            await callback.answer(f'У страны {country} уже есть президент {named}')
        cur.close()

async def country_velikobritanya(callback: types.CallbackQuery):
    await check_user(callback)
    user_id = callback.from_user.id
    country = callback.data
    with sqlite3.connect('game/data.db', timeout=10) as conn:
        cur = conn.cursor()
        president, cash = cur.execute("""SELECT president_country, cash FROM users WHERE user_id = ?""",
                                      (user_id,)).fetchone()
        cost, country_presedent = cur.execute("""SELECT cost, president FROM countries WHERE country = ?""",
                                              (country,)).fetchone()
        if president == 'нет' and cash >= cost and country_presedent == 0:
            # Вычет денег из баланса
            cur.execute("""UPDATE users SET cash = ?, president_country = ?, citizen_country = ? WHERE user_id = ?""",
                        (cash - cost, country, country, user_id))
            conn.commit()
            # Страна обрела президента
            cur.execute("""UPDATE countries SET president = ? WHERE country = ?""", (user_id, country))
            conn.commit()
            await bot.send_message(callback.message.chat.id,
                                   text=f'@{callback.from_user.username} успешно купил страну - {country}! 🌍\n' + ''.join(
                                       msg_data))
        elif cash < cost:
            await callback.answer(f'Ваш нужно ещё {cost - cash:n}$')
        elif president != 'нет':
            pres_count = cur.execute("""SELECT president_country FROM users WHERE user_id = ?""", (user_id,)).fetchone()
            await callback.answer(f'Вы уже президент страны {pres_count[0]}')
        elif country_presedent != 0:
            id_user = cur.execute("""SELECT president FROM countries WHERE country = ?""", (country,)).fetchone()
            idname = await bot.get_chat(id_user[0])
            named = quote_html(idname.username)
            await callback.answer(f'У страны {country} уже есть президент {named}')
        cur.close()

async def country_germany(callback: types.CallbackQuery):
    await check_user(callback)
    user_id = callback.from_user.id
    country = callback.data
    with sqlite3.connect('game/data.db', timeout=10) as conn:
        cur = conn.cursor()
        president, cash = cur.execute("""SELECT president_country, cash FROM users WHERE user_id = ?""",
                                      (user_id,)).fetchone()
        cost, country_presedent = cur.execute("""SELECT cost, president FROM countries WHERE country = ?""",
                                              (country,)).fetchone()
        if president == 'нет' and cash >= cost and country_presedent == 0:
            # Вычет денег из баланса
            cur.execute("""UPDATE users SET cash = ?, president_country = ?, citizen_country = ? WHERE user_id = ?""",
                        (cash - cost, country, country, user_id))
            conn.commit()
            # Страна обрела президента
            cur.execute("""UPDATE countries SET president = ? WHERE country = ?""", (user_id, country))
            conn.commit()
            await bot.send_message(callback.message.chat.id,
                                   text=f'@{callback.from_user.username} успешно купил страну - {country}! 🌍\n' + ''.join(
                                       msg_data))
        elif cash < cost:
            await callback.answer(f'Ваш нужно ещё {cost - cash:n}$')
        elif president != 'нет':
            pres_count = cur.execute("""SELECT president_country FROM users WHERE user_id = ?""", (user_id,)).fetchone()
            await callback.answer(f'Вы уже президент страны {pres_count[0]}')
        elif country_presedent != 0:
            id_user = cur.execute("""SELECT president FROM countries WHERE country = ?""", (country,)).fetchone()
            idname = await bot.get_chat(id_user[0])
            named = quote_html(idname.username)
            await callback.answer(f'У страны {country} уже есть президент {named}')
        cur.close()

async def country_italia(callback: types.CallbackQuery):
    await check_user(callback)
    user_id = callback.from_user.id
    country = callback.data
    with sqlite3.connect('game/data.db', timeout=10) as conn:
        cur = conn.cursor()
        president, cash = cur.execute("""SELECT president_country, cash FROM users WHERE user_id = ?""",
                                      (user_id,)).fetchone()
        cost, country_presedent = cur.execute("""SELECT cost, president FROM countries WHERE country = ?""",
                                              (country,)).fetchone()
        if president == 'нет' and cash >= cost and country_presedent == 0:
            # Вычет денег из баланса
            cur.execute("""UPDATE users SET cash = ?, president_country = ?, citizen_country = ? WHERE user_id = ?""",
                        (cash - cost, country, country, user_id))
            conn.commit()
            # Страна обрела президента
            cur.execute("""UPDATE countries SET president = ? WHERE country = ?""", (user_id, country))
            conn.commit()
            await bot.send_message(callback.message.chat.id,
                                   text=f'@{callback.from_user.username} успешно купил страну - {country}! 🌍\n' + ''.join(
                                       msg_data))
        elif cash < cost:
            await callback.answer(f'Ваш нужно ещё {cost - cash:n}$')
        elif president != 'нет':
            pres_count = cur.execute("""SELECT president_country FROM users WHERE user_id = ?""", (user_id,)).fetchone()
            await callback.answer(f'Вы уже президент страны {pres_count[0]}')
        elif country_presedent != 0:
            id_user = cur.execute("""SELECT president FROM countries WHERE country = ?""", (country,)).fetchone()
            idname = await bot.get_chat(id_user[0])
            named = quote_html(idname.username)
            await callback.answer(f'У страны {country} уже есть президент {named}')
        cur.close()

async def country_kazahstan(callback: types.CallbackQuery):
    await check_user(callback)
    user_id = callback.from_user.id
    country = callback.data
    with sqlite3.connect('game/data.db', timeout=10) as conn:
        cur = conn.cursor()
        president, cash = cur.execute("""SELECT president_country, cash FROM users WHERE user_id = ?""",
                                      (user_id,)).fetchone()
        cost, country_presedent = cur.execute("""SELECT cost, president FROM countries WHERE country = ?""",
                                              (country,)).fetchone()
        if president == 'нет' and cash >= cost and country_presedent == 0:
            # Вычет денег из баланса
            cur.execute("""UPDATE users SET cash = ?, president_country = ?, citizen_country = ? WHERE user_id = ?""",
                        (cash - cost, country, country, user_id))
            conn.commit()
            # Страна обрела президента
            cur.execute("""UPDATE countries SET president = ? WHERE country = ?""", (user_id, country))
            conn.commit()
            await bot.send_message(callback.message.chat.id,
                                   text=f'@{callback.from_user.username} успешно купил страну - {country}! 🌍\n' + ''.join(
                                       msg_data))
        elif cash < cost:
            await callback.answer(f'Ваш нужно ещё {cost - cash:n}$')
        elif president != 'нет':
            pres_count = cur.execute("""SELECT president_country FROM users WHERE user_id = ?""", (user_id,)).fetchone()
            await callback.answer(f'Вы уже президент страны {pres_count[0]}')
        elif country_presedent != 0:
            id_user = cur.execute("""SELECT president FROM countries WHERE country = ?""", (country,)).fetchone()
            idname = await bot.get_chat(id_user[0])
            named = quote_html(idname.username)
            await callback.answer(f'У страны {country} уже есть президент {named}')
        cur.close()

async def country_china(callback: types.CallbackQuery):
    await check_user(callback)
    user_id = callback.from_user.id
    country = callback.data
    with sqlite3.connect('game/data.db', timeout=10) as conn:
        cur = conn.cursor()
        president, cash = cur.execute("""SELECT president_country, cash FROM users WHERE user_id = ?""",
                                      (user_id,)).fetchone()
        cost, country_presedent = cur.execute("""SELECT cost, president FROM countries WHERE country = ?""",
                                              (country,)).fetchone()
        if president == 'нет' and cash >= cost and country_presedent == 0:
            # Вычет денег из баланса
            cur.execute("""UPDATE users SET cash = ?, president_country = ?, citizen_country = ? WHERE user_id = ?""",
                        (cash - cost, country, country, user_id))
            conn.commit()
            # Страна обрела президента
            cur.execute("""UPDATE countries SET president = ? WHERE country = ?""", (user_id, country))
            conn.commit()
            await bot.send_message(callback.message.chat.id,
                                   text=f'@{callback.from_user.username} успешно купил страну - {country}! 🌍\n' + ''.join(
                                       msg_data))
        elif cash < cost:
            await callback.answer(f'Ваш нужно ещё {cost - cash:n}$')
        elif president != 'нет':
            pres_count = cur.execute("""SELECT president_country FROM users WHERE user_id = ?""", (user_id,)).fetchone()
            await callback.answer(f'Вы уже президент страны {pres_count[0]}')
        elif country_presedent != 0:
            id_user = cur.execute("""SELECT president FROM countries WHERE country = ?""", (country,)).fetchone()
            idname = await bot.get_chat(id_user[0])
            named = quote_html(idname.username)
            await callback.answer(f'У страны {country} уже есть президент {named}')
        cur.close()

async def country_kolumbia(callback: types.CallbackQuery):
    await check_user(callback)
    user_id = callback.from_user.id
    country = callback.data
    with sqlite3.connect('game/data.db', timeout=10) as conn:
        cur = conn.cursor()
        president, cash = cur.execute("""SELECT president_country, cash FROM users WHERE user_id = ?""",
                                      (user_id,)).fetchone()
        cost, country_presedent = cur.execute("""SELECT cost, president FROM countries WHERE country = ?""",
                                              (country,)).fetchone()
        if president == 'нет' and cash >= cost and country_presedent == 0:
            # Вычет денег из баланса
            cur.execute("""UPDATE users SET cash = ?, president_country = ?, citizen_country = ? WHERE user_id = ?""",
                        (cash - cost, country, country, user_id))
            conn.commit()
            # Страна обрела президента
            cur.execute("""UPDATE countries SET president = ? WHERE country = ?""", (user_id, country))
            conn.commit()
            await bot.send_message(callback.message.chat.id,
                                   text=f'@{callback.from_user.username} успешно купил страну - {country}! 🌍\n' + ''.join(
                                       msg_data))
        elif cash < cost:
            await callback.answer(f'Ваш нужно ещё {cost - cash:n}$')
        elif president != 'нет':
            pres_count = cur.execute("""SELECT president_country FROM users WHERE user_id = ?""", (user_id,)).fetchone()
            await callback.answer(f'Вы уже президент страны {pres_count[0]}')
        elif country_presedent != 0:
            id_user = cur.execute("""SELECT president FROM countries WHERE country = ?""", (country,)).fetchone()
            idname = await bot.get_chat(id_user[0])
            named = quote_html(idname.username)
            await callback.answer(f'У страны {country} уже есть президент {named}')
        cur.close()

async def country_niderlandi(callback: types.CallbackQuery):
    await check_user(callback)
    user_id = callback.from_user.id
    country = callback.data
    with sqlite3.connect('game/data.db', timeout=10) as conn:
        cur = conn.cursor()
        president, cash = cur.execute("""SELECT president_country, cash FROM users WHERE user_id = ?""",
                                      (user_id,)).fetchone()
        cost, country_presedent = cur.execute("""SELECT cost, president FROM countries WHERE country = ?""",
                                              (country,)).fetchone()
        if president == 'нет' and cash >= cost and country_presedent == 0:
            # Вычет денег из баланса
            cur.execute("""UPDATE users SET cash = ?, president_country = ?, citizen_country = ? WHERE user_id = ?""",
                        (cash - cost, country, country, user_id))
            conn.commit()
            # Страна обрела президента
            cur.execute("""UPDATE countries SET president = ? WHERE country = ?""", (user_id, country))
            conn.commit()
            await bot.send_message(callback.message.chat.id,
                                   text=f'@{callback.from_user.username} успешно купил страну - {country}! 🌍\n' + ''.join(
                                       msg_data))
        elif cash < cost:
            await callback.answer(f'Ваш нужно ещё {cost - cash:n}$')
        elif president != 'нет':
            pres_count = cur.execute("""SELECT president_country FROM users WHERE user_id = ?""", (user_id,)).fetchone()
            await callback.answer(f'Вы уже президент страны {pres_count[0]}')
        elif country_presedent != 0:
            id_user = cur.execute("""SELECT president FROM countries WHERE country = ?""", (country,)).fetchone()
            idname = await bot.get_chat(id_user[0])
            named = quote_html(idname.username)
            await callback.answer(f'У страны {country} уже есть президент {named}')
        cur.close()

async def country_polsha(callback: types.CallbackQuery):
    await check_user(callback)
    user_id = callback.from_user.id
    country = callback.data
    with sqlite3.connect('game/data.db', timeout=10) as conn:
        cur = conn.cursor()
        president, cash = cur.execute("""SELECT president_country, cash FROM users WHERE user_id = ?""",
                                      (user_id,)).fetchone()
        cost, country_presedent = cur.execute("""SELECT cost, president FROM countries WHERE country = ?""",
                                              (country,)).fetchone()
        if president == 'нет' and cash >= cost and country_presedent == 0:
            # Вычет денег из баланса
            cur.execute("""UPDATE users SET cash = ?, president_country = ?, citizen_country = ? WHERE user_id = ?""",
                        (cash - cost, country, country, user_id))
            conn.commit()
            # Страна обрела президента
            cur.execute("""UPDATE countries SET president = ? WHERE country = ?""", (user_id, country))
            conn.commit()
            await bot.send_message(callback.message.chat.id,
                                   text=f'@{callback.from_user.username} успешно купил страну - {country}! 🌍\n' + ''.join(
                                       msg_data))
        elif cash < cost:
            await callback.answer(f'Ваш нужно ещё {cost - cash:n}$')
        elif president != 'нет':
            pres_count = cur.execute("""SELECT president_country FROM users WHERE user_id = ?""", (user_id,)).fetchone()
            await callback.answer(f'Вы уже президент страны {pres_count[0]}')
        elif country_presedent != 0:
            id_user = cur.execute("""SELECT president FROM countries WHERE country = ?""", (country,)).fetchone()
            idname = await bot.get_chat(id_user[0])
            named = quote_html(idname.username)
            await callback.answer(f'У страны {country} уже есть президент {named}')
        cur.close()

async def country_russia(callback: types.CallbackQuery):
    await check_user(callback)
    user_id = callback.from_user.id
    country = callback.data
    with sqlite3.connect('game/data.db', timeout=10) as conn:
        cur = conn.cursor()
        president, cash = cur.execute("""SELECT president_country, cash FROM users WHERE user_id = ?""",
                                      (user_id,)).fetchone()
        cost, country_presedent = cur.execute("""SELECT cost, president FROM countries WHERE country = ?""",
                                              (country,)).fetchone()
        if president == 'нет' and cash >= cost and country_presedent == 0:
            # Вычет денег из баланса
            cur.execute("""UPDATE users SET cash = ?, president_country = ?, citizen_country = ? WHERE user_id = ?""",
                        (cash - cost, country, country, user_id))
            conn.commit()
            # Страна обрела президента
            cur.execute("""UPDATE countries SET president = ? WHERE country = ?""", (user_id, country))
            conn.commit()
            await bot.send_message(callback.message.chat.id,
                                   text=f'@{callback.from_user.username} успешно купил страну - {country}! 🌍\n' + ''.join(
                                       msg_data))
        elif cash < cost:
            await callback.answer(f'Ваш нужно ещё {cost - cash:n}$')
        elif president != 'нет':
            pres_count = cur.execute("""SELECT president_country FROM users WHERE user_id = ?""", (user_id,)).fetchone()
            await callback.answer(f'Вы уже президент страны {pres_count[0]}')
        elif country_presedent != 0:
            id_user = cur.execute("""SELECT president FROM countries WHERE country = ?""", (country,)).fetchone()
            idname = await bot.get_chat(id_user[0])
            named = quote_html(idname.username)
            await callback.answer(f'У страны {country} уже есть президент {named}')
        cur.close()

async def country_ruminia(callback: types.CallbackQuery):
    await check_user(callback)
    user_id = callback.from_user.id
    country = callback.data
    with sqlite3.connect('game/data.db', timeout=10) as conn:
        cur = conn.cursor()
        president, cash = cur.execute("""SELECT president_country, cash FROM users WHERE user_id = ?""",
                                      (user_id,)).fetchone()
        cost, country_presedent = cur.execute("""SELECT cost, president FROM countries WHERE country = ?""",
                                              (country,)).fetchone()
        if president == 'нет' and cash >= cost and country_presedent == 0:
            # Вычет денег из баланса
            cur.execute("""UPDATE users SET cash = ?, president_country = ?, citizen_country = ? WHERE user_id = ?""",
                        (cash - cost, country, country, user_id))
            conn.commit()
            # Страна обрела президента
            cur.execute("""UPDATE countries SET president = ? WHERE country = ?""", (user_id, country))
            conn.commit()
            await bot.send_message(callback.message.chat.id,
                                   text=f'@{callback.from_user.username} успешно купил страну - {country}! 🌍\n' + ''.join(
                                       msg_data))
        elif cash < cost:
            await callback.answer(f'Ваш нужно ещё {cost - cash:n}$')
        elif president != 'нет':
            pres_count = cur.execute("""SELECT president_country FROM users WHERE user_id = ?""", (user_id,)).fetchone()
            await callback.answer(f'Вы уже президент страны {pres_count[0]}')
        elif country_presedent != 0:
            id_user = cur.execute("""SELECT president FROM countries WHERE country = ?""", (country,)).fetchone()
            idname = await bot.get_chat(id_user[0])
            named = quote_html(idname.username)
            await callback.answer(f'У страны {country} уже есть президент {named}')
        cur.close()

async def country_usa(callback: types.CallbackQuery):
    await check_user(callback)
    user_id = callback.from_user.id
    country = callback.data
    with sqlite3.connect('game/data.db', timeout=10) as conn:
        cur = conn.cursor()
        president, cash = cur.execute("""SELECT president_country, cash FROM users WHERE user_id = ?""",
                                      (user_id,)).fetchone()
        cost, country_presedent = cur.execute("""SELECT cost, president FROM countries WHERE country = ?""",
                                              (country,)).fetchone()
        if president == 'нет' and cash >= cost and country_presedent == 0:
            # Вычет денег из баланса
            cur.execute("""UPDATE users SET cash = ?, president_country = ?, citizen_country = ? WHERE user_id = ?""",
                        (cash - cost, country, country, user_id))
            conn.commit()
            # Страна обрела президента
            cur.execute("""UPDATE countries SET president = ? WHERE country = ?""", (user_id, country))
            conn.commit()
            await bot.send_message(callback.message.chat.id,
                                   text=f'@{callback.from_user.username} успешно купил страну - {country}! 🌍\n' + ''.join(
                                       msg_data))
        elif cash < cost:
            await callback.answer(f'Ваш нужно ещё {cost - cash:n}$')
        elif president != 'нет':
            pres_count = cur.execute("""SELECT president_country FROM users WHERE user_id = ?""", (user_id,)).fetchone()
            await callback.answer(f'Вы уже президент страны {pres_count[0]}')
        elif country_presedent != 0:
            id_user = cur.execute("""SELECT president FROM countries WHERE country = ?""", (country,)).fetchone()
            idname = await bot.get_chat(id_user[0])
            named = quote_html(idname.username)
            await callback.answer(f'У страны {country} уже есть президент {named}')
        cur.close()

async def country_turkey(callback: types.CallbackQuery):
    await check_user(callback)
    user_id = callback.from_user.id
    country = callback.data
    with sqlite3.connect('game/data.db', timeout=10) as conn:
        cur = conn.cursor()
        president, cash = cur.execute("""SELECT president_country, cash FROM users WHERE user_id = ?""",
                                      (user_id,)).fetchone()
        cost, country_presedent = cur.execute("""SELECT cost, president FROM countries WHERE country = ?""",
                                              (country,)).fetchone()
        if president == 'нет' and cash >= cost and country_presedent == 0:
            # Вычет денег из баланса
            cur.execute("""UPDATE users SET cash = ?, president_country = ?, citizen_country = ? WHERE user_id = ?""",
                        (cash - cost, country, country, user_id))
            conn.commit()
            # Страна обрела президента
            cur.execute("""UPDATE countries SET president = ? WHERE country = ?""", (user_id, country))
            conn.commit()
            await bot.send_message(callback.message.chat.id,
                                   text=f'@{callback.from_user.username} успешно купил страну - {country}! 🌍\n' + ''.join(
                                       msg_data))
        elif cash < cost:
            await callback.answer(f'Ваш нужно ещё {cost - cash:n}$')
        elif president != 'нет':
            pres_count = cur.execute("""SELECT president_country FROM users WHERE user_id = ?""", (user_id,)).fetchone()
            await callback.answer(f'Вы уже президент страны {pres_count[0]}')
        elif country_presedent != 0:
            id_user = cur.execute("""SELECT president FROM countries WHERE country = ?""", (country,)).fetchone()
            idname = await bot.get_chat(id_user[0])
            named = quote_html(idname.username)
            await callback.answer(f'У страны {country} уже есть президент {named}')
        cur.close()

async def country_ukraine(callback: types.CallbackQuery):
    await check_user(callback)
    user_id = callback.from_user.id
    country = callback.data
    with sqlite3.connect('game/data.db', timeout=10) as conn:
        cur = conn.cursor()
        president, cash = cur.execute("""SELECT president_country, cash FROM users WHERE user_id = ?""",
                                      (user_id,)).fetchone()
        cost, country_presedent = cur.execute("""SELECT cost, president FROM countries WHERE country = ?""",
                                              (country,)).fetchone()
        if president == 'нет' and cash >= cost and country_presedent == 0:
            # Вычет денег из баланса
            cur.execute("""UPDATE users SET cash = ?, president_country = ?, citizen_country = ? WHERE user_id = ?""",
                        (cash - cost, country, country, user_id))
            conn.commit()
            # Страна обрела президента
            cur.execute("""UPDATE countries SET president = ? WHERE country = ?""", (user_id, country))
            conn.commit()
            await bot.send_message(callback.message.chat.id,
                                   text=f'@{callback.from_user.username} успешно купил страну - {country}! 🌍\n' + ''.join(
                                       msg_data))
        elif cash < cost:
            await callback.answer(f'Ваш нужно ещё {cost - cash:n}$')
        elif president != 'нет':
            pres_count = cur.execute("""SELECT president_country FROM users WHERE user_id = ?""", (user_id,)).fetchone()
            await callback.answer(f'Вы уже президент страны {pres_count[0]}')
        elif country_presedent != 0:
            id_user = cur.execute("""SELECT president FROM countries WHERE country = ?""", (country,)).fetchone()
            idname = await bot.get_chat(id_user[0])
            named = quote_html(idname.username)
            await callback.answer(f'У страны {country} уже есть президент {named}')
        cur.close()

async def country_france(callback: types.CallbackQuery):
    await check_user(callback)
    user_id = callback.from_user.id
    country = callback.data
    with sqlite3.connect('game/data.db', timeout=10) as conn:
        cur = conn.cursor()
        president, cash = cur.execute("""SELECT president_country, cash FROM users WHERE user_id = ?""",
                                      (user_id,)).fetchone()
        cost, country_presedent = cur.execute("""SELECT cost, president FROM countries WHERE country = ?""",
                                              (country,)).fetchone()
        if president == 'нет' and cash >= cost and country_presedent == 0:
            # Вычет денег из баланса
            cur.execute("""UPDATE users SET cash = ?, president_country = ?, citizen_country = ? WHERE user_id = ?""",
                        (cash - cost, country, country, user_id))
            conn.commit()
            # Страна обрела президента
            cur.execute("""UPDATE countries SET president = ? WHERE country = ?""", (user_id, country))
            conn.commit()
            await bot.send_message(callback.message.chat.id,
                                   text=f'@{callback.from_user.username} успешно купил страну - {country}! 🌍\n' + ''.join(
                                       msg_data))
        elif cash < cost:
            await callback.answer(f'Ваш нужно ещё {cost - cash:n}$')
        elif president != 'нет':
            pres_count = cur.execute("""SELECT president_country FROM users WHERE user_id = ?""", (user_id,)).fetchone()
            await callback.answer(f'Вы уже президент страны {pres_count[0]}')
        elif country_presedent != 0:
            id_user = cur.execute("""SELECT president FROM countries WHERE country = ?""", (country,)).fetchone()
            idname = await bot.get_chat(id_user[0])
            named = quote_html(idname.username)
            await callback.answer(f'У страны {country} уже есть президент {named}')
        cur.close()

async def country_japan(callback: types.CallbackQuery):
    await check_user(callback)
    user_id = callback.from_user.id
    country = callback.data
    with sqlite3.connect('game/data.db', timeout=10) as conn:
        cur = conn.cursor()
        president, cash = cur.execute("""SELECT president_country, cash FROM users WHERE user_id = ?""",
                                      (user_id,)).fetchone()
        cost, country_presedent = cur.execute("""SELECT cost, president FROM countries WHERE country = ?""",
                                              (country,)).fetchone()
        if president == 'нет' and cash >= cost and country_presedent == 0:
            # Вычет денег из баланса
            cur.execute("""UPDATE users SET cash = ?, president_country = ?, citizen_country = ? WHERE user_id = ?""",
                        (cash - cost, country,country, user_id))
            conn.commit()
            # Страна обрела президента
            cur.execute("""UPDATE countries SET president = ? WHERE country = ?""", (user_id, country))
            conn.commit()
            await bot.send_message(callback.message.chat.id,
                                   text=f'@{callback.from_user.username} успешно купил страну - {country}! 🌍\n' + ''.join(
                                       msg_data))
        elif cash < cost:
            await callback.answer(f'Ваш нужно ещё {cost - cash:n}$')
        elif president != 'нет':
            pres_count = cur.execute("""SELECT president_country FROM users WHERE user_id = ?""", (user_id,)).fetchone()
            await callback.answer(f'Вы уже президент страны {pres_count[0]}')
        elif country_presedent != 0:
            id_user = cur.execute("""SELECT president FROM countries WHERE country = ?""", (country,)).fetchone()
            idname = await bot.get_chat(id_user[0])
            named = quote_html(idname.username)
            await callback.answer(f'У страны {country} уже есть президент {named}')
        cur.close()

# Регистрация хендлеров
def register_handlers_countries(dp: Dispatcher):
    dp.register_callback_query_handler(country_armenia, text='Армения')
    dp.register_callback_query_handler(country_belarus, text='Беларусь')
    dp.register_callback_query_handler(country_brazilia, text='Бразилия')
    dp.register_callback_query_handler(country_velikobritanya, text='Великобритания')
    dp.register_callback_query_handler(country_germany, text='Германия')
    dp.register_callback_query_handler(country_italia, text='Италия')
    dp.register_callback_query_handler(country_kazahstan, text='Казахстан')
    dp.register_callback_query_handler(country_china, text='Китай')
    dp.register_callback_query_handler(country_kolumbia, text='Колумбия')
    dp.register_callback_query_handler(country_niderlandi, text='Нидерланды')
    dp.register_callback_query_handler(country_polsha, text='Польша')
    dp.register_callback_query_handler(country_ruminia, text='Россия')
    dp.register_callback_query_handler(country_ruminia, text='Румыния')
    dp.register_callback_query_handler(country_usa, text='США')
    dp.register_callback_query_handler(country_turkey, text='Турция')
    dp.register_callback_query_handler(country_ukraine, text='Украина')
    dp.register_callback_query_handler(country_france, text='Франция')
    dp.register_callback_query_handler(country_japan, text='Япония')
