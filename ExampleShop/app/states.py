import aiogram
from aiogram import Bot,Dispatcher,executor,types
from aiogram.dispatcher.filters.state import State,StatesGroup

class NewOrder(StatesGroup):
    type= State()
    name = State()
    desc = State()
    price = State()
    photo = State()