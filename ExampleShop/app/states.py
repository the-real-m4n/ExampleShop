import aiogram
from aiogram import Bot,Dispatcher,executor,types
from aiogram.dispatcher.filters.state import State,StatesGroup

class NewItem(StatesGroup):
    type= State()
    name = State()
    desc = State()
    price = State()
    photo = State()
    existence=State()

class NewOrder(StatesGroup):
    type= State()
    item= State()
    count= State()
    back_check=State()
    

class RegOrder(StatesGroup):
    adress= State()
    phone_number=State()
    comment=State()

class DeleteItem(StatesGroup):
    type=State()
    item_id=State()