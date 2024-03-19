import aiogram
from aiogram.types import ReplyKeyboardMarkup,InlineKeyboardButton,InlineKeyboardMarkup

main_keyboard=ReplyKeyboardMarkup(resize_keyboard=True)# основная клавиатура
main_keyboard.add("Catalog").add('Card').add("Contacts")

main_admin=ReplyKeyboardMarkup(resize_keyboard=True)# клавиатура для админа
main_admin.add("Catalog").add('Card').add("Contacts").add("Admin Panel")

admin_panel=ReplyKeyboardMarkup(resize_keyboard=True)# админ панель
admin_panel.add("Add product").add('Delete product').add('Change Prise')

catalog_list= InlineKeyboardMarkup(row_width=4)
catalog_list.add(InlineKeyboardButton(text='Товар 1', callback_data='Товар 1'),
                 InlineKeyboardButton(text='Товар 2', callback_data='Товар 2'),
                 InlineKeyboardButton(text='Товар 3', callback_data='Товар 3'),
                 InlineKeyboardButton(text='Товар 4', callback_data='Товар 4'),
                 InlineKeyboardButton(text='Товар 5', callback_data='Товар 5'),
                 InlineKeyboardButton(text='Товар 6', callback_data='Товар 6'))

cancel=ReplyKeyboardMarkup(resize_keyboard=True)
cancel.add("Отмена")

back=ReplyKeyboardMarkup(resize_keyboard=True)
back.add("Добавить товар").add('Каталог')
