from bot import dp
from aiogram import executor
from loguru import logger
import asyncio


if __name__ == "__main__":

    logger.info('Bot is starting.')

    executor.start_polling(dp, loop=asyncio.get_event_loop(), skip_updates=True)
