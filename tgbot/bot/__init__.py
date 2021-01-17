from aiogram import Bot, Dispatcher, types
import os
from aiogram.contrib.fsm_storage.mongo import MongoStorage
import uvloop


API_TOKEN = os.environ['BOT_API_KEY']

bot = Bot(token=API_TOKEN, parse_mode='html')

storage = MongoStorage(host=os.environ['MONGODB_HOSTNAME'],
                       port=os.environ['MONGODB_PORT'],
                       username=os.environ['MONGODB_USERNAME'],
                       password=os.environ['MONGODB_PASSWORD'])

dp = Dispatcher(bot, storage=storage)

uvloop.install()


from bot import modules
from tasks import *
