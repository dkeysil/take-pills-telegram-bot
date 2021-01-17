from bot import dp, types
from motor_client import SingletonClient
from loguru import logger


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    """
    Catches start command and add uses in DB
    :param message:
    :return:
    """
    logger.info(f"/start user_id={message.from_user.id}")
