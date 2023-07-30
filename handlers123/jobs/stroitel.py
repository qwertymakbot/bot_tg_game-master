from bot import *


# /build Список объектов ожидающих строителей
async def build(message):
    await check_user(message)
    with sqlite3.connect('game/data.db', timeout=10) as conn:
        cur = conn.cursor()
        id_build = message.get_args().split()
        if len(id_build) == 0:  # Если аргументов нет
            job = cur.execute("""SELECT job FROM users WHERE user_id = ?""", (message.from_user.id,)).fetchone()
            if job[0] == 'Строитель':
                arr = next(os.walk(f'./game/build_bus'))[2]
                if len(arr) != 0:  # Если список не пустой
                    data = []
                    data.append('🧱 Список активных строек:\n')
                    for i in arr:
                        with open(f'./game/build_bus/{i}', 'r', encoding='utf-8') as f:
                            build_data = json.load(f)
                            if build_data['isbuilding'] == False and len(build_data['builders']) < build_data[
                                'need_builder']:
                                data.append(f"⚠️ ID стройки: {str(i).replace('.json', '')}\n")
                                data.append(f'👷‍♂️ Нужно строителей: {build_data["need_builder"]}\n')
                                data.append(f'💰 Оплата по окончанию стройки: {build_data["builder_pay"]}$\n')
                    data.append(f'\n❗️ Чтобы устроится на стройку, введите команду /build 1 - где 1 это ID стройки')
                    await message.answer(''.join(data))
                else:
                    await message.answer('🧱 В данный момент активных строек нет!')
            else:
                await message.answer(f'@{message.from_user.username}, эта команда доступна только строителям!')
        else:
            try:
                id_build = int(id_build[0])
                job = cur.execute("""SELECT job FROM users WHERE user_id = ?""", (message.from_user.id,)).fetchone()
                if job[0] == 'Строитель':
                    try:
                        with open(f'./game/build_bus/{id_build}.json', 'r', encoding='utf-8') as f:
                            isWorking = cur.execute("""SELECT working FROM users WHERE user_id = ?""",
                                                    (message.from_user.id,)).fetchone()
                            if not isWorking[0]:  # Если не работает
                                build_data = json.load(f)
                                if not build_data['isbuilding'] and len(build_data['builders']) < build_data[
                                    'need_builder']:  # Стройка в режиме ожидания и нуждается в строителях
                                    builders = build_data['builders']  # Список строителей

                                    cur = conn.cursor()
                                    cur.execute("""CREATE TABLE IF NOT EXISTS builders_work(
                                                                    builder INT,
                                                                    boss INT)""")
                                    bilder = cur.execute("""SELECT boss FROM builders_work WHERE builder = ?""",
                                                         (message.from_user.id,)).fetchone()
                                    if bilder is None:  # Если пользователь не устроен на стройке
                                        # запись строителя и заказчика в бд
                                        cur.execute("""INSERT INTO builders_work VALUES(?,?)""",
                                                    (message.from_user.id, id_build))
                                        conn.commit()
                                        # запись строителя в список json
                                        builders.append(message.from_user.id)
                                        build_data['builders'] = builders
                                        with open(f'./game/build_bus/{id_build}.json', 'w', encoding='utf-8') as f:
                                            json.dump(build_data, f)
                                        boss = cur.execute("""SELECT username FROM users WHERE user_id = ?""",
                                                           (id_build,)).fetchone()
                                        await message.answer(
                                            f'@{message.from_user.username}, вы успешно устроились на объект к @{boss[0]} 🧱\n\n'
                                            f'❗️ Ожидайте пока все соберутся и руководитель начнет стройку, ваш гонорар при окончании {build_data["builder_pay"]}$')
                                    else:
                                        await message.answer(
                                            f'@{message.from_user.username}, вы уже устроены на стройке {bilder[0]}')
                                else:
                                    await message.answer(f'@{message.from_user.username}, стройка уже неактуальна')
                            else:
                                await message.answer(f'@{message.from_user.username}, для начала окончите работу!')

                    except:
                        await message.answer(f'@{message.from_user.username}, данная стройка не существует!')
                else:
                    await message.answer(f'@{message.from_user.username}, эта команда доступна только строителям!')
            except:
                await message.answer(f'@{message.from_user.username}, пример ввода: /build 123123')
        cur.close()

# /leave_build Уйти со стройки
async def leave_build(message):
    await check_user(message)
    with sqlite3.connect('game/data.db', timeout=10) as conn:
        cur = conn.cursor()
        job = cur.execute("""SELECT job FROM users WHERE user_id = ?""", (message.from_user.id,)).fetchone()
        if job[0] == 'Строитель':
            boss = cur.execute("""SELECT boss FROM builders_work WHERE builder = ?""", (message.from_user.id,)).fetchone()
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
                await message.answer(f'@{message.from_user.username}, вы не работаете ни на каком строительном объекте!')
        else:
            await message.answer(f'@{message.from_user.username}, данная команда доступна только строителям!')
        cur.close()

def register_handlers_stroitel(dp: Dispatcher):
    dp.register_message_handler(build, commands='build')
    dp.register_message_handler(leave_build, commands='leave_build')