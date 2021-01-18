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

    db = SingletonClient.get_data_base()

    user = await db.Users.find_one({
        "telegram_id": message.from_user.id
    })

    if user:
        return await message.answer("You are already registered in the bot.")

    result = await db.Users.insert_one({
        "telegram_id": message.from_user.id,
        "first_name": message.from_user.first_name,
        "last_name": message.from_user.last_name,
        "username": message.from_user.username
    })
    logger.info(f"/start user_id={message.from_user.id} insert_one result={result.acknowledged} id={result.inserted_id}")

    await message.answer('Welcome, try to add new pill via /new.')
