from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

#token = '1850330075:AAGzUXvuKKCIfMo-UuAWngb4w53mqZZfLW8'

# sherlock
token = '1798112999:AAErW6n1joExRb_DgjzIOfHJyjsXUZCzxT4'
#testobot
#token = '6262973132:AAHRHU9cXBSC2r4bq9sLn7znnPglLQDyGYI'
bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())


