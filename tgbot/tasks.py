import aiocron
from bot import bot, types
from motor_client import SingletonClient
from loguru import logger
from bson import ObjectId
import asyncio
from datetime import time, datetime


@aiocron.crontab("*/5 * * * *")
async def pills_check():
    """
    Check pills from db every 5 minutes and send notifications if need
    :return:
    """
    logger.info("pills check started")
    db = SingletonClient.get_data_base()
    now = time(datetime.now().hour, datetime.now().minute)

    if now == time(0, 0):
        result = await db.Pills.update_many({}, {
            "$set": {
                "time_status": []
            }
        })

    # todo сделать цикл пробегающийся по таблеткам и отправлять напоминания с кнопкой подветрждения, если не нажата, то присылать еще раз

    async for pill in db.Pills.find():
        user = await db.Users.find_one({
            "_id": ObjectId(pill.get("user"))
        })

        time_status = pill.get("time_status")
        for num, ti in enumerate(pill.get("time_list")):
            t = time.fromisoformat(ti)
            if t > now:
                continue
            try:
                status = time_status[num]
            except IndexError:
                status = False
                time_status.append(False)

            if status:
                # if user accept time don't send notification
                continue

            if now > time(t.hour + 1, t.minute):
                # If more than one hour has elapsed after taking the pill and the person has not taken it
                time_status[num] = True
            else:
                text = "You have to take <b>{}</b> pill at {}.".format(pill.get("title"), ti)
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("I took 💊", callback_data=f"took,{pill.get('_id')},{ti}"))
                await bot.send_message(user.get("telegram_id"), text=text, reply_markup=markup)

            result = await db.Pills.update_one({
                "_id": ObjectId(pill.get("_id"))
            },
                {
                    "$set": {
                        "time_status": time_status
                    }
                })

            logger.info(f"user_id={user.get('telegram_id')} pill_id={pill.get('_id')} "
                        f"update_one result={result.acknowledged} time_status={time_status}")
