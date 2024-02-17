import aiogram
from aiogram import Bot,Dispatcher,executor,types
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup,InlineKeyboardButton
from dotenv import load_dotenv
import os

load_dotenv()
bot=Bot(os.getenv("TOKEN"))
dp=Dispatcher(bot=bot)

main_keyboard=ReplyKeyboardMarkup(resize_keyboard=True)# основная клавиатура
main_keyboard.add("Catalog").add('Card').add("Contacts")

main_admin=ReplyKeyboardMarkup(resize_keyboard=True)# клавиатура для админа
main_admin.add("Catalog").add('Card').add("Contacts").add("Admin Panel")

admin_panel=ReplyKeyboardMarkup(resize_keyboard=True)# админ панель
admin_panel.add("Add product").add('Delete product').add('Change Prise')

catalog_list=InlineKeyboardMarkup(row_width=3)
catalog_list.add(InlineKeyboardButton(text='Роллы',), 
                 InlineKeyboardButton(text='Суши'),
                 InlineKeyboardButton(text=''))

@dp.message_handler(commands=['start'])
async def start(message: types.message):
    if message.from_user.id==int(os.getenv("ADMIN_ID")):# проверка на пользователя на роль админа
        await message.answer(f'Hello Admin!', reply_markup=main_admin)# вызов клавиатуры для админа
    else:
        await message.answer(f'{message.from_user.first_name}, Hello', reply_markup=main_keyboard)#вызов клавиатуры для пользователя

@dp.message_handler(text='Admin Panel')# обработчик для админ панели
async def contacts(message: types.message):
    if message.from_user.id==int(os.getenv("ADMIN_ID")):
        await message.answer(f'Welcome to admin panel ',reply_markup=admin_panel) 
    else:
        await message.reply("You don`t have access")

@dp.message_handler(text='Contacts')#обработчик для кнопки контакты
async def contacts(message: types.message):
    await message.answer(f'контакты продавца')

@dp.message_handler(text='Card')#обработчик для корзины
async def card(message: types.message):
    await message.answer(f'test2')

@dp.message_handler(text='Catalog')# обработчик для каталога
async def contacts(message: types.message):
    await message.answer(f'test 1')

@dp.message_handler()#обработчик для неверных запросов
async def wrong_command(message: types.Message):
    await message.reply("I dont understand you")


if __name__=='__main__':
    executor.start_polling(dp)