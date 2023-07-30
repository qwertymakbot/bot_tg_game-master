from bs4 import BeautifulSoup
import requests
from bot import Dispatcher
async def joke(message):
    url = 'https://nekdo.ru/random/'
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    text = soup.find('div', class_='text').text
    await message.reply(text)

def register_handlers_countries(dp: Dispatcher):
    dp.register_message_handler(joke, content_types='text',
                                text=['Шутка', 'шутка', 'анекдот', 'Анекдот'])