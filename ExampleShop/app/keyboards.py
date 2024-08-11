import aiogram
from aiogram.types import ReplyKeyboardMarkup,InlineKeyboardButton,InlineKeyboardMarkup

main_keyboard=ReplyKeyboardMarkup(resize_keyboard=True)# основная клавиатура
main_keyboard.add("Заказать").add('Корзина').add("Контакты").add("Назад")

main_admin=ReplyKeyboardMarkup(resize_keyboard=True)# клавиатура для админа
main_admin.add("Заказать").add('Корзина').add("Контакты").add("Меню Администратора")

admin_panel=ReplyKeyboardMarkup(resize_keyboard=True)# админ панель
admin_panel.add("Добавить позицию").add('Удалить позицию').add('Изменить цену').add("Назад").add("Изменить наличие")

catalog_list= InlineKeyboardMarkup(row_width=4)
catalog_list.add(InlineKeyboardButton(text='Товар 1', callback_data='Товар 1'),
                 InlineKeyboardButton(text='Товар 2', callback_data='Товар 2'),
                 InlineKeyboardButton(text='Товар 3', callback_data='Товар 3'),
                 InlineKeyboardButton(text='Товар 4', callback_data='Товар 4'),
                 InlineKeyboardButton(text='Товар 5', callback_data='Товар 5'),
                 InlineKeyboardButton(text='Товар 6', callback_data='Товар 6'),
                 InlineKeyboardButton(text="Назад", callback_data="Назад"))

cancel=ReplyKeyboardMarkup(resize_keyboard=True)
cancel.add("Назад")

back=ReplyKeyboardMarkup(resize_keyboard=True)
back.add("Добавить товар").add('Каталог').add("Меню")

card_menu=ReplyKeyboardMarkup(resize_keyboard=True)#Клавиатура для корзины 
card_menu.add("Оформить заказ").add("Назад")

existence_kb=InlineKeyboardMarkup(row_width=2)
existence_kb.add(InlineKeyboardButton(text='В наличии', callback_data=1),
                 InlineKeyboardButton(text="Нет в наличии", callback_data=0))
