from aiogram import Bot, Dispatcher, types
import os
from aiogram.contrib.fsm_storage.mongo import MongoStorage
import uvloop
from aiogram_logging import Logger, InfluxSender
from aiogram.dispatcher.middlewares import BaseMiddleware


API_TOKEN = os.environ['BOT_API_KEY']

bot = Bot(token=API_TOKEN, parse_mode='html')

sender = InfluxSender(host='172.17.0.1',
                      db='telegram',
                      username='user',
                      password='password')
log = Logger(sender_class=sender)

storage = MongoStorage(host=os.environ['MONGODB_HOSTNAME'],
                       port=os.environ['MONGODB_PORT'],
                       username=os.environ['MONGODB_USERNAME'],
                       password=os.environ['MONGODB_PASSWORD'])

dp = Dispatcher(bot, storage=storage)


class StatMiddleware(BaseMiddleware):

    def __init__(self):
        super(StatMiddleware, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        await log.write_logs(self._manager.bot.id, message, parse_text=True)


dp.middleware.setup(StatMiddleware())
uvloop.install()


from bot import modules
from tasks import *
