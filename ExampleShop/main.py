import aiogram,logging,os
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot,Dispatcher,executor,types
from aiogram.dispatcher.filters.state import State,StatesGroup
from aiogram.dispatcher import FSMContext
from app import keyboards as kb
from app import db,states
from dotenv import load_dotenv

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
        await message.answer(f'{message.from_user.first_name}, Hello', reply_markup=kb.main_keyboard)#вызов клавиатуры для пользователя

@dp.message_handler(text='Admin Panel')# обработчик для админ панели
async def contacts(message: types.message):
    if message.from_user.id==int(os.getenv("ADMIN_ID")):
        await message.answer(f'Welcome to admin panel ',reply_markup=kb.admin_panel) 
    else:
        await message.reply("You don`t have access")

@dp.message_handler(text='Add product')
async def add_item(message: types.message):
    if message.from_user.id==int(os.getenv("ADMIN_ID")):
        await states.NewOrder.type.set()
        await message.answer(f'Выберите тип товара : ',reply_markup=kb.catalog_list )
    else:
        await message.reply("You don`t have access")

@dp.callback_query_handler(state=states.NewOrder.type)
async def add_item_type(call: types.CallbackQuery, state:FSMContext):
    async with state.proxy() as data:
        data['type']=call.data
    await call.message.answer(f'Напишите название товара: ', reply_markup=kb.cancel)
    await states.NewOrder.next()


@dp.message_handler(state=states.NewOrder.name)
async def add_item_name(message: types.Message, state:FSMContext):
    if message.text=="Отмена":
        await state.finish()
        await message.answer('Отмена!',reply_markup=kb.admin_panel)
    else:
        async with state.proxy() as data:
            data['name']=message.text
        await message.answer(f'Напишите описание товара', reply_markup=kb.cancel) 
        await states.NewOrder.next()

@dp.message_handler(state=states.NewOrder.desc)
async def add_item_desc(message: types.Message, state:FSMContext):
    if message.text=="Отмена":
        await state.finish()
        await message.answer('Отмена!',reply_markup=kb.admin_panel)
    else:
        async with state.proxy() as data:
            data['desc']=message.text
        await message.answer(f'Напишите цену товара', reply_markup=kb.cancel) 
        await states.NewOrder.next()

@dp.message_handler(state=states.NewOrder.price)
async def add_item_price(message: types.Message, state:FSMContext):
    if message.text=="Отмена":
        await state.finish()
        await message.answer('Отмена!',reply_markup=kb.admin_panel)
    else:    
        async with state.proxy() as data:
            data['price']=message.text
        await message.answer(f'Добавьте фото товара', reply_markup=kb.cancel) 
        await states.NewOrder.next()

@dp.message_handler(lambda message: not message.photo, state=states.NewOrder.photo)
async def add_item_photo_check(message: types.Message):
    await message.answer(f'Это не фото')
    
    
@dp.message_handler(content_types=['photo'], state=states.NewOrder.photo)
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

@dp.message_handler()#обработчик для неверных запросов
async def wrong_command(message: types.Message):
    await message.reply("I dont understand you")

@dp.callback_query_handler()
async def callback_query_keyboard(callback_query: types.CallbackQuery):
    if callback_query.data == "Товар 1":
        await bot.send_message(chat_id=callback_query.from_user.id, text="Товар 1 успешно добавлен в корзину")
    elif callback_query.data == "Товар 2":
        await bot.send_message(chat_id=callback_query.from_user.id, text="Товар 2 успешно добавлен в корзину")
    elif callback_query.data == "Товар 3":
        await bot.send_message(chat_id=callback_query.from_user.id, text="Товар 3 успешно добавлен в корзину")
    elif callback_query.data == "Товар 4":
        await bot.send_message(chat_id=callback_query.from_user.id, text="Товар 4 успешно добавлен в корзину")
    elif callback_query.data == "Товар 5":
        await bot.send_message(chat_id=callback_query.from_user.id, text="Товар 5 успешно добавлен в корзину")
    elif callback_query.data == "Товар 6":
        await bot.send_message(chat_id=callback_query.from_user.id, text="Товар 6 успешно добавлен в корзину")

if __name__=='__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)