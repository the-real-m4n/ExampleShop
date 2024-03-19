import aiogram
from aiogram import Bot,Dispatcher,executor,types
from aiogram.dispatcher.filters.state import State,StatesGroup

class NewItem(StatesGroup):
    type= State()
    name = State()
    desc = State()
    price = State()
    photo = State()

class NewOrder(StatesGroup):
    type= State()
    item= State()
    count= State()
    back_check=State()
    
class InfoCard(StatesGroup):
    adress = State()
    phone = State()
    comment = State()
