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
    await states.NewOrder.type.set()

@dp.message_handler()#обработчик для неверных запросов
async def wrong_command(message: types.Message):
    await message.reply("I dont understand you")


@dp.callback_query_handler(state=states.NewOrder.type)
async def chose_item_type(call: types.CallbackQuery, state:FSMContext):
    async with state.proxy() as data:
        data['type']=call.data
    items = await db.add_item_to_card(state)
    for item in items:
        name, desc, price, photo_id = item
        make_order=InlineKeyboardMarkup(row_width=1)
        make_order.add(InlineKeyboardButton(text='Заказать', callback_data=str(name)))
        await call.message.answer_photo(photo_id, caption=f'Название: {name}\n Описание: {desc}\n Цена: {price}',reply_markup=make_order)
    await states.NewOrder.next()

@dp.message_handler(state=states.NewOrder.name)
async def chose_item(message: types.Message, state:FSMContext):
    pass# привязать клаву-счетчик и сделать запрос на следующий товар
""".add(InlineKeyboardButton('+', callback_data=f'{counter+1}')).add(InlineKeyboardButton('-', callback_data=f'{counter-1}'))"""



if __name__=='__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)