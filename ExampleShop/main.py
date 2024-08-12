import aiogram,logging,os
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot,Dispatcher,executor,types
from aiogram.dispatcher.filters.state import State,StatesGroup
from aiogram.dispatcher.filters import Text
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



@dp.message_handler(text='Меню Администратора')# обработчик для админ панели
async def contacts(message: types.message):
    if message.from_user.id==int(os.getenv("ADMIN_ID")):
        await message.answer(f'Welcome to admin panel ',reply_markup=kb.admin_panel) 
    else:
        await message.reply("You don`t have access")

@dp.message_handler(text='Удалить позицию')#Удаление позиции из меню
async def Delete_Position_handler(message: types.message):
    await message.answer(f'Наше меню',reply_markup=kb.catalog_list)
    await states.DeleteItem.type.set()

@dp.callback_query_handler(state=states.DeleteItem.type)
async def Pick_type(call: types.CallbackQuery, state:FSMContext):
    async with state.proxy() as data:
        data['type']=call.data
        print("TYPE ITEM TO DELETE", )
    items = await db.find_item_to_delete_or_chage_existence(state)
    for item in items:
        item_id,name,photo_id = item
        print("item to delete:",item) 
        delete_item = InlineKeyboardMarkup(row_width=1)
        delete_item.add(InlineKeyboardButton(text='Удалить', callback_data=str(item_id)))
        await call.message.answer_photo(photo_id, caption=f'Название: {name}', reply_markup=delete_item)
        await states.DeleteItem.next()

@dp.callback_query_handler(state=states.DeleteItem.item_id)
async def deleting_item(call: types.CallbackQuery, state:FSMContext):
        async with state.proxy() as data:
            data['item_id']=call.data
            print("ID TO DELETE",data)
            copy_data=dict(data)
            await db.del_item(copy_data)
            await call.message.answer("Позиция успешно удалена")
            await state.finish()

@dp.message_handler(text="Изменить наличие")                               # стоп лист 
async def change_stop_list(message: types.message):
    await message.answer(f'Выберите товар для изменения наличия',reply_markup=kb.catalog_list)
    await states.StopList.type.set()

@dp.callback_query_handler(state=states.StopList.type)
async def Pick_type_to_change_stop_list(call: types.CallbackQuery, state:FSMContext):
    async with state.proxy() as data:
        data['type']=call.data
        print("TYPE ITEM TO Chage stop list ",data )
    items = await db.find_item_to_delete_or_chage_existence(state)
    for item in items:
        item_id,name,photo_id = item
        print("item to stop list:",item) 
        chage_existence_item = InlineKeyboardMarkup(row_width=1)
        chage_existence_item.add(InlineKeyboardButton(text='Изменить', callback_data=str(item_id)))
        await call.message.answer_photo(photo_id, caption=f'Название: {name}', reply_markup=chage_existence_item)
    await states.StopList.next()

@dp.callback_query_handler(state=states.StopList.item_id)
async def pick_item_to_chage_state(call: types.CallbackQuery, state:FSMContext):
    async with state.proxy() as data:
        data['item_id']=call.data
        print("ID ITEM TO Chage stop list ",data )
        await call.message.answer("Укажите наличие",reply_markup=kb.existence_kb)
        await states.StopList.next()


@dp.callback_query_handler(state=states.StopList.existence)
async def chage_item_state(call: types.CallbackQuery, state:FSMContext):
    async with state.proxy() as data:
        data['existence']=call.data
        print("ID ITEM TO Chage stop list ",data )
        copy_data=data
        await call.message.answer("Изменения сохранены!",reply_markup=kb.main_admin)
        try:
            await db.change_existence(copy_data)
            await state.finish()
        except:
            await call.message.answer("Произошла ошибка!")
        

@dp.message_handler(text="Редактировать товар")                        # Редактирование товаров 
async def chage_item_handler(message: types.message):
    await message.answer(f'Выберите товар для изменения',reply_markup=kb.catalog_list)
    await states.ChangeItem.type.set()

@dp.callback_query_handler(state=states.ChangeItem.type)
async def Pick_type_to_change(call: types.CallbackQuery, state:FSMContext):
    async with state.proxy() as data:
        data['type']=call.data
        print("TYPE ITEM TO Chage stop list ",data )
    items = await db.find_item(state)
    for item in items:
        item_id,name,desc,price,photo_id = item[:5]
        print("items to change:",item)
        pick_item=InlineKeyboardMarkup(row_width=1)
        pick_item.add(InlineKeyboardButton(text='Редактировать', callback_data=str(item_id)))
        await call.message.answer_photo(photo_id, caption=f'Название: {name}\nОписание: {desc}\nЦена: {price}', reply_markup=pick_item)
    await states.ChangeItem.next()

@dp.callback_query_handler(state=states.ChangeItem.item_id)
async def Pick_item_id_to_change(call: types.CallbackQuery, state:FSMContext):
     async with state.proxy() as data:
        data['item_id'] = call.data
        print('ITEM ID TO CHAGE :' ,data['item_id'])
        chage_item_kb=InlineKeyboardMarkup(row_width=3)
        chage_item_kb.add(InlineKeyboardButton(text="Наименование",callback_data='name'),
                          InlineKeyboardButton(text="Описание",    callback_data='desc'),
                          InlineKeyboardButton(text="Стоймость",   callback_data='price'),
                          InlineKeyboardButton(text='Фото',        callback_data='photo')) 
        await call.message.answer(f'Выберите характеристику которую нужно изменить',reply_markup=chage_item_kb)
        await states.ChangeItem.next()

@dp.callback_query_handler(state=states.ChangeItem.field_to_edit)
async def get_field_to_chage_item(call: types.CallbackQuery, state:FSMContext):
    async with state.proxy() as data:
        data['field_to_edit'] = call.data
        print('field to edit TO CHAGE :' ,data['field_to_edit'])
        await call.message.answer(f'Введите новое значение')
        await states.ChangeItem.next()

@dp.message_handler(content_types=['photo','text'], state=states.ChangeItem.new_value)
async def get_new_value_to_change_item(message: types.Message, state:FSMContext):
    async with state.proxy() as data:
        if data['field_to_edit']=='price':
            if not message.text.isdigit():
                await message.reply("Введите корректное количество")
                message = await dp.bot.next_update()
            else:
                data['new_value']= message.text
        elif data['field_to_edit']=='photo':
            data['new_value']=message.photo[0].file_id
        else:
            data['new_value']= message.text

        copy_data=dict(data)
        print("COPY : ", copy_data)
        await db.change_item(copy_data)
        await message.answer(f"Позизция успешно изменена",reply_markup=kb.admin_panel)
        await state.finish()




@dp.message_handler(text='Добавить позицию')                           # Добавление новых товаров 
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
            while not message.text.isdigit():
                await message.reply("Введите корректное количество")
                message = await dp.bot.next_update()
        await message.answer(f'Добавьте фото товара', reply_markup=kb.cancel) 
        await states.NewItem.next()

@dp.message_handler(lambda message: not message.photo, state=states.NewItem.photo)# проверка на фото
async def add_item_photo_check(message: types.Message):
    await message.answer(f'Это не фото')
     
@dp.message_handler(content_types=['photo'], state=states.NewItem.photo)#Добавление фото товара и сохранение в базу данных
async def add_item_photo(message: types.Message, state:FSMContext):
    async with state.proxy() as data:
        data['photo']=message.photo[0].file_id
    #
    await message.answer(f'Укажите наличие', reply_markup=kb.existence_kb) 
    await states.NewItem.next()

@dp.callback_query_handler(state=states.NewItem.existence)
async def add_item_existence(call: types.CallbackQuery, state:FSMContext):
    async with state.proxy() as data:
        data["existence"]=call.data
        print(data)
        data_copy = dict(data)
        await call.message.answer("Товар успешно добавлен!",reply_markup=kb.admin_panel)
        await db.add_item(data_copy)
        await state.finish()
        


@dp.message_handler(text='Контакты')#обработчик для кнопки контакты
async def contacts(message: types.message):
    await message.answer(f'контакты продавца')

@dp.message_handler(Text(equals='Корзина'))  # Обработчик для кнопки корзина
async def card(message: types.Message):
    try:
        user_id = message.from_user.id
        
        # Получение содержимого корзины
        items_list, counts_list = await db.show_card(user_id)
        print("Items List:", items_list)
        print("Counts List:", counts_list)
        
        await message.answer('Ваша корзина', reply_markup=kb.card_menu)
        
        if items_list:  # Проверка на пустой список
            message_text = "Содержимое вашей корзины:\n\n"
            total_price = 0
            for item_id, count in zip(items_list, counts_list):
                # Получение информации о товаре по item_id
                item = await db.get_item_details(item_id)
                if item:
                    name, desc, price, photo = item
                    total_price += int(price) * int(count)
                    message_text += (f"Название: {name}\nОписание: {desc}\nЦена: {int(price) * int(count)}\n"
                                     f"Количество: {count}\n\n")
                    
                    keyboard = InlineKeyboardMarkup(row_width=2)
                    keyboard.add(
                        InlineKeyboardButton(text="-", callback_data=f"decrease_{item_id}"),
                        InlineKeyboardButton(text="+", callback_data=f"increase_{item_id}")
                    )

                    # Отправка сообщения пользователю
                    await message.answer_photo(photo, caption=message_text, reply_markup=keyboard)
                
        else:
            await message.answer("Ваша корзина пуста.", reply_markup=kb.main_keyboard)
    
    except Exception as e:
        print(f"An error occurred: {e}")

    


async def update_cart_message(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    message = callback_query.message

    # Получение содержимого корзины
    items_list, counts_list = await db.show_card(user_id)
    
    if items_list:
        total_price = 0
        message_text = ""
        keyboard = InlineKeyboardMarkup(row_width=2)
        
        for item_id, count in zip(items_list, counts_list):
            # Получение информации о товаре по item_id
            item = await db.get_item_details(item_id)
            if item:
                name, desc, price, photo = item
                item_total_price = int(price) * int(count)
                total_price += item_total_price
                message_text += (f"Название: {name}\nОписание: {desc}\nЦена за единицу: {price}\n"
                                 f"Количество: {count}\nИтоговая цена: {item_total_price}\n\n")
                
                # Добавление кнопок для каждого товара
                item_keyboard = InlineKeyboardMarkup(row_width=2)
                item_keyboard.add(
                    InlineKeyboardButton(text="-", callback_data=f"decrease_{item_id}"),
                    InlineKeyboardButton(text="+", callback_data=f"increase_{item_id}")
                )
                
                # Отправка сообщения с фотографией товара и кнопками
                await message.answer_photo(photo=photo, caption=message_text, reply_markup=item_keyboard)
                message_text = ""  # Очищаем текст сообщения для следующего товара

        # Отправка общего итога
        await callback_query.message.answer(f'Итого: {total_price}')
    else:
        await message.edit_text("Ваша корзина пуста.")

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('increase_'))
async def increase_item(callback_query: types.CallbackQuery):
    item_id = int(callback_query.data.split('_')[1])
    user_id = callback_query.from_user.id

    # Увеличить количество товара в корзине
    await db.update_item_count(user_id, item_id, increase=True)

    # Обновить сообщение с корзиной
    await update_cart_message(callback_query)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('decrease_'))
async def decrease_item(callback_query: types.CallbackQuery):
    item_id = int(callback_query.data.split('_')[1])
    user_id = callback_query.from_user.id

    # Уменьшить количество товара в корзине
    await db.update_item_count(user_id, item_id, increase=False)

    # Обновить сообщение с корзиной
    await update_cart_message(callback_query)

@dp.message_handler(lambda message: message.text.lower() == 'назад', state='*')
async def cancel_action(message: types.Message, state: FSMContext):
    await message.answer("главное меню.", reply_markup=kb.main_keyboard)
    await state.finish()    

@dp.message_handler(text="Оформить заказ")      # Начало сценария оформления заказа
async def RegestrationOrder(message:types.message):
    await message.answer(f'Укажите адрес доставки')
    await states.RegOrder.adress.set()
        
@dp.message_handler(state=states.RegOrder.adress)                 #Добавление номера адресса для оформления заказа
async def add_adress(message: types.Message, state:FSMContext):
    if message.text=="Отмена":
        await state.finish()
        await message.answer('Отмена!',reply_markup=kb.main_keyboard)
    else:
        async with state.proxy() as data:
            data['adress']=message.text
        await message.answer(f'Укажите номер телефона начиная с цифры 8',reply_markup=kb.cancel)
        await states.RegOrder.next()

@dp.message_handler(lambda message: not (len(message.text) == 11 and message.text.isdigit() and not message.text.startswith('7')), state=states.RegOrder.phone_number)
async def phone_check(message: types.Message):
    if len(message.text) != 11:
        await message.answer('Вы ввели неправильный номер: длина должна быть 11 символов.')
    elif not message.text.isdigit():
        await message.answer('Вы ввели неправильный номер: номер должен содержать только цифры.')



@dp.message_handler(state=states.RegOrder.phone_number)           # Добавление номера телефона для оформления заказа
async def add_phone(message: types.Message, state:FSMContext):
    if message.text=="Отмена":
        await state.finish()
        await message.answer('Отмена!',reply_markup=kb.main_keyboard)
    else:
        async with state.proxy() as data:
            data['phone']=message.text
        await message.answer(f'Добавьте комментарий к заказу',reply_markup=kb.cancel)
        await states.RegOrder.next()

@dp.message_handler(state=states.RegOrder.comment)                 #Добавления коммента для оформления заказа
async def add_comments(message: types.Message, state:FSMContext):
    if message.text=="Отмена":
        await state.finish()
        await message.answer('Отмена!',reply_markup=kb.main_keyboard)
    else:
        async with state.proxy() as data:
            data['comments']=message.text
        await message.answer(f'Заказ передан для оформления!',reply_markup=kb.main_keyboard)
        print(data)
        await db.add_order_info(state,user_id=message.from_user.id)
        await state.finish()


    
@dp.message_handler(text='Заказать')                           # обработчик для каталога
async def MakeOrder(message: types.message):
    await message.answer(f'Наше меню',reply_markup=kb.catalog_list)
    await states.NewOrder.type.set()                          # Начало нового state






@dp.callback_query_handler(state=states.NewOrder.type)         #Вывод каталога по выбранной категории
async def chose_item_type(call: types.CallbackQuery, state:FSMContext):
    async with state.proxy() as data:
        data['type'] = call.data
        print(data)
    if data['type']=="Назад" :
        await call.message.answer("Меню",reply_markup=kb.main_keyboard)
        await state.finish()

    items = await db.find_item(state)
    
    for item in items:
        item_id,name, desc, price, photo_id,existence = item
        print("item :",item) 
        make_order = InlineKeyboardMarkup(row_width=1)
        make_order.add(InlineKeyboardButton(text='Заказать', callback_data=str(item_id)))
        if existence==1:
            await call.message.answer_photo(photo_id, caption=f'Название: {name}\nОписание: {desc}\nЦена: {price}', reply_markup=make_order)
        else:
            await call.message.answer_photo(photo_id, caption=f'Название: {name}\nОписание: {desc}\nЦена: {price} \n\ нет в наличии')
    await call.message.answer(f'Вы выбрали категорию"{data["type"]}',reply_markup=kb.cancel)
    await states.NewOrder.item.set()



@dp.callback_query_handler(state=states.NewOrder.item)
async def chose_item(call: types.CallbackQuery, state:FSMContext):
    async with state.proxy() as data:
        data['item_id'] = call.data
        print(data['item_id'])
        if not data['item_id'].isdigit():
            await call.message.answer("Не верный выбор")
        print(data)
    await call.message.answer(f'Укажите количество',reply_markup=kb.cancel)
    await states.NewOrder.next()



@dp.message_handler(state=states.NewOrder.count)                     #указание количества товара
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
        await message.answer(f'Товар успешно добавлен в корзину',reply_markup=kb.back)
        await states.NewOrder.next()
        #await state.reset_data() 



@dp.message_handler(state=states.NewOrder.back_check)             #продолжение процесса сбора корзины 
async def back_check(message: types.Message,state:FSMContext):
    if message.text=="Добавить товар":
        items = await db.find_item(state)
        for item in items:
            item_id,name, desc, price, photo_id,existence = item
            print("item :",item) 
            make_order = InlineKeyboardMarkup(row_width=1)
            make_order.add(InlineKeyboardButton(text='Заказать', callback_data=str(item_id)))
            if existence==1:
                await message.answer_photo(photo_id, caption=f'Название: {name}\nОписание: {desc}\nЦена: {price}', reply_markup=make_order)
            else:
                await message.answer_photo(photo_id, caption=f'Название: {name}\nОписание: {desc}\nЦена: {price} \n\ нет в наличии')
    
       
            await states.NewOrder.item.set()
    elif message.text=="Каталог":
        await message.answer("Каталог",reply_markup=kb.catalog_list)
        await states.NewOrder.first()
    elif message.text=="Меню":
        await message.answer("Меню",reply_markup=kb.main_keyboard)
        await state.finish()


@dp.message_handler()                                         #обработчик для неверных запросов
async def wrong_command(message: types.Message):
    await message.reply("Я не понимаю тебя")

if __name__=='__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)

#прикрутить юкассу и немного доделать оформление заказа (итогувую стоймость)
#подумать как реализовать отправку заказов(чеков на заказ) в ресторан (мб рассылка по почте или на аккаунт тг)
