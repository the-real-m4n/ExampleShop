import aiogram
from aiogram import Bot,Dispatcher,executor,types
from dotenv import load_dotenv
import os

load_dotenv()

bot=Bot(os.getenv("TOKEN"))
dp=Dispatcher(bot=bot)

@dp.message_handler(commands=['start'])
async def start(message: types.message):
    await message.answer(f'{message.from_user.first_name}, Hello')

@dp.message_handler()
async def wrong_command(message: types.Message):
    await message.reply("I dont understand you")


if __name__=='__main__':
    executor.start_polling(dp)