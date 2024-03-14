import aiogram,logging,os
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot,Dispatcher,executor,types
from aiogram.dispatcher.filters.state import State,StatesGroup
from aiogram.dispatcher import FSMContext
from app import keyboards as kb
from app import db,states
from dotenv import load_dotenv
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

storage=MemoryStorage()
load_dotenv()
bot=Bot(os.getenv("TOKEN"))
dp=Dispatcher(bot=bot, storage=storage)
logging.basicConfig(level=logging.INFO)

async def on_startup(_):
    await db.start_db()
    print("Bot is working")


@dp.message_handler(commands=['start'])
async def start(message: types.message):
    await db.add_id(user_id=message.from_user.id)
    if message.from_user.id==int(os.getenv("ADMIN_ID")):# проверка на пользователя на роль админа
        await message.answer(f'Hello Admin!', reply_markup=kb.main_admin)# вызов клавиатуры для админа
    else:
        await message.answer(f'{message.from_user.id}, Hello', reply_markup=kb.main_keyboard)#вызов клавиатуры для пользователя

@dp.message_handler(text='Admin Panel')# обработчик для админ панели
async def contacts(message: types.message):
    if message.from_user.id==int(os.getenv("ADMIN_ID")):
        await message.answer(f'Welcome to admin panel ',reply_markup=kb.admin_panel) 
    else:
        await message.reply("You don`t have access")

@dp.message_handler(text='Add product')# Добавление новых товаров 
async def add_item(message: types.message):
    if message.from_user.id==int(os.getenv("ADMIN_ID")):
        await states.NewItem.type.set()
        await message.answer(f'Выберите тип товара : ',reply_markup=kb.catalog_list )
    else:
        await message.reply("You don`t have access")

@dp.callback_query_handler(state=states.NewItem.type)# Добавление типа товара и запрос на название
async def add_item_type(call: types.CallbackQuery, state:FSMContext):
    async with state.proxy() as data:
        data['type']=call.data
    await call.message.answer(f'Напишите название товара: ', reply_markup=kb.cancel)
    await states.NewItem.next()


@dp.message_handler(state=states.NewItem.name)# Добавление название товара и запрос на описание
async def add_item_name(message: types.Message, state:FSMContext):
    if message.text=="Отмена":
        await state.finish()
        await message.answer('Отмена!',reply_markup=kb.admin_panel)
    else:
        async with state.proxy() as data:
            data['name']=message.text
        await message.answer(f'Напишите описание товара', reply_markup=kb.cancel) 
        await states.NewItem.next()

@dp.message_handler(state=states.NewItem.desc)# Добавление описание товара и запрос на цену
async def add_item_desc(message: types.Message, state:FSMContext):
    if message.text=="Отмена":
        await state.finish()
        await message.answer('Отмена!',reply_markup=kb.admin_panel)
    else:
        async with state.proxy() as data:
            data['desc']=message.text
        await message.answer(f'Напишите цену товара', reply_markup=kb.cancel) 
        await states.NewItem.next()

@dp.message_handler(state=states.NewItem.price)# Добавление цены товара и запрос на фото
async def add_item_price(message: types.Message, state:FSMContext):
    if message.text=="Отмена":
        await state.finish()
        await message.answer('Отмена!',reply_markup=kb.admin_panel)
    else:    
        async with state.proxy() as data:
            data['price']=message.text
        await message.answer(f'Добавьте фото товара', reply_markup=kb.cancel) 
        await states.NewItem.next()

@dp.message_handler(lambda message: not message.photo, state=states.NewItem.photo)# проверка на фото
async def add_item_photo_check(message: types.Message):
    await message.answer(f'Это не фото')
    
    
@dp.message_handler(content_types=['photo'], state=states.NewItem.photo)#Добавление фото товара и сохранение в базу данных
async def add_item_photo(message: types.Message, state:FSMContext):
    async with state.proxy() as data:
        data['photo']=message.photo[0].file_id
    await db.add_item(state)
    await message.answer(f'Товар успешно создан!', reply_markup=kb.admin_panel) 
    await state.finish()


@dp.message_handler(text='Contacts')#обработчик для кнопки контакты
async def contacts(message: types.message):
    await message.answer(f'контакты продавца')

@dp.message_handler(text='Card')#обработчик для корзины
async def card(message: types.message):
    await message.answer(f'Корзина')

@dp.message_handler(text='Catalog')# обработчик для каталога
async def contacts(message: types.message):
    await message.answer(f'Каталог',reply_markup=kb.catalog_list)
    await states.NewOrder.type.set()# Начало нового state

@dp.message_handler()#обработчик для неверных запросов
async def wrong_command(message: types.Message):
    await message.reply("I dont understand you")

@dp.callback_query_handler(state=states.NewOrder.type)
async def chose_item_type(call: types.CallbackQuery, state:FSMContext):
    async with state.proxy() as data:
        data['type'] = call.data
        print(data)
    items = await db.find_item(state)
    
    for item in items:
        item_id,name, desc, price, photo_id = item
        print("item :",item)
        make_order = InlineKeyboardMarkup(row_width=1)
        make_order.add(InlineKeyboardButton(text='Заказать', callback_data=str(item_id)))
        await call.message.answer_photo(photo_id, caption=f'Название: {name}\nОписание: {desc}\nЦена: {price}', reply_markup=make_order)
    await states.NewOrder.item.set()

@dp.callback_query_handler(state=states.NewOrder.item)
async def chose_item(call: types.CallbackQuery, state:FSMContext):
    async with state.proxy() as data:
        data['item_id'] = call.data
        while not data['item_id'].isdigit():
            await call.message.answer("Не верный выбор")
            #message = await dp.bot.next_update()
        print(data)
    await call.message.answer(f'Укажите количество',reply_markup=kb.cancel)
    await states.NewOrder.next()


@dp.message_handler(state=states.NewOrder.count)
async def chose_count(message: types.Message, state:FSMContext):
    async with state.proxy() as data:
        while not message.text.isdigit():
            await message.reply("Введите корректное количество")
            message = await dp.bot.next_update()
           
        data['count'] = message.text
        data['user_id'] = message.from_user.id
        await state.update_data(count=data['count'])
        print(data)
        await db.add_item_to_card(state,data['user_id'])
        await message.answer(f'Товар успешно доабвлен в корзину',reply_markup=kb.back)
        #if message.text == "Назад":
            #await state.finish() 
            #await message.answer(f'Каталог',reply_markup=kb.catalog_list)  Не работает кнопка не срабатывает
            #await states.NewOrder.type.set()
            #return
        await states.NewOrder.type.set()
        
@dp.message_handler(state=states.InfoCard.adress)
async def add_adress(message: types.Message, state:FSMContext):
    if message.text=="Отмена":
        await state.finish()
        await message.answer('Отмена!',reply_markup=kb.main_keyboard)
    else:
        async with state.proxy() as data:
            data['adress']=message.text
        await message.answer(f'Укажите номер телефона с использованием +7',reply_markup=kb.cancel)
        await states.NewOrder.next()

@dp.message_handler(lambda message: not len(message.text)==12, state=states.InfoCard.phone)# проверка количество цифр в номере
async def phone_check(message: types.Message):
    if len(message.text)!=12:
        await message.answer(f'Вы ввели неправильный номер')


@dp.message_handler(state=states.InfoCard.phone)
async def add_phone(message: types.Message, state:FSMContext):
    if message.text=="Отмена":
        await state.finish()
        await message.answer('Отмена!',reply_markup=kb.main_keyboard)
    else:
        async with state.proxy() as data:
            data['phone']=message.text
        await message.answer(f'Добавьте комментарий к заказу',reply_markup=kb.cancel)
        await states.NewOrder.next()

@dp.message_handler(state=states.InfoCard.phone)
async def add_comments(message: types.Message, state:FSMContext):
    if message.text=="Отмена":
        await state.finish()
        await message.answer('Отмена!',reply_markup=kb.main_keyboard)
    else:
        async with state.proxy() as data:
            data['comments']=message.text
        await message.answer(f'Заказ передан для оформления!')
        await state.finish()
#сделать метод в бд для добавления в корзину и переделать методы так чтобы всю инфу по типу адреса и т.п запрашивало в корзине а не в каталоге 
if __name__=='__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)