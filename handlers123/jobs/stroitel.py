from bot import bot, username, username_2, res_database, database, Dispatcher


# /build Список объектов ожидающих строителей
async def build(message):
    ...


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
