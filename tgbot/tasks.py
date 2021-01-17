import aiocron
from bot import bot
from motor_client import SingletonClient
from loguru import logger
from bson import ObjectId
import asyncio


@aiocron.crontab("*/5 * * * *")
async def pills_check():
    """
    Check pills from db every 5 minutes and send notifications if need
    :return:
    """
    logger.info("pills check started")
