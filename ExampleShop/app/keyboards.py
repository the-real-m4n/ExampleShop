import aiogram
from aiogram.types import ReplyKeyboardMarkup,InlineKeyboardButton,InlineKeyboardMarkup

main_keyboard=ReplyKeyboardMarkup(resize_keyboard=True)# основная клавиатура
main_keyboard.add("Catalog").add('Card').add("Contacts").add("Назад")

main_admin=ReplyKeyboardMarkup(resize_keyboard=True)# клавиатура для админа
main_admin.add("Catalog").add('Card').add("Contacts").add("Admin Panel")

admin_panel=ReplyKeyboardMarkup(resize_keyboard=True)# админ панель
admin_panel.add("Add product").add('Delete product').add('Change Prise').add("Назад")

catalog_list= InlineKeyboardMarkup(row_width=4)
catalog_list.add(InlineKeyboardButton(text='Товар 1', callback_data='Товар 1'),
                 InlineKeyboardButton(text='Товар 2', callback_data='Товар 2'),
                 InlineKeyboardButton(text='Товар 3', callback_data='Товар 3'),
                 InlineKeyboardButton(text='Товар 4', callback_data='Товар 4'),
                 InlineKeyboardButton(text='Товар 5', callback_data='Товар 5'),
                 InlineKeyboardButton(text='Товар 6', callback_data='Товар 6'),
                 InlineKeyboardButton(text="Назад", callback_data="Назад"))

cancel=ReplyKeyboardMarkup(resize_keyboard=True)
cancel.add("Отмена")

back=ReplyKeyboardMarkup(resize_keyboard=True)
back.add("Добавить товар").add('Каталог').add("Меню")

card_menu=ReplyKeyboardMarkup(resize_keyboard=True)#Клавиатура для корзины 
card_menu.add("Удалить товар").add("Оформить заказ").add("Назад")

