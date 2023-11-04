from create_bot import dp, bot
from aiogram import types
import g4f
from filters.filters import IsQuestions
from bs4 import BeautifulSoup
import requests


# GPT3.5 TURBO
@dp.message_handler(IsQuestions())
async def text(message: types.Message):
    prompt = message.text
    if not prompt:
        await message.answer('Вы задали пустой запрос.')
    else:
        msg = await message.reply('Ищу ответ на ваш вопрос!')
        await run_provider(prompt.replace('Бот ', '').replace('бот ', ''), msg)


async def run_provider(prompt, msg):
    try:
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.gpt_35_turbo,
            messages=[{"role": "user", "content": prompt}]
            #provider=g4f.Provider.ChatgptAi
        )
        await bot.edit_message_text(response, chat_id=msg.chat.id, message_id=msg.message_id)
    except Exception as e:
        await bot.edit_message_text(e, chat_id=msg.chat.id, message_id=msg.message_id)


# Анекдот шутка
@dp.message_handler(content_types='text', text=['Шутка', 'шутка', 'анекдот', 'Анекдот'])
async def joke(message):
    url = 'https://nekdo.ru/random/'
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    text = soup.find('div', class_='text').text
    await message.reply(text)
