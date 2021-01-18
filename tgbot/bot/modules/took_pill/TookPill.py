from bot import dp, types
from motor_client import SingletonClient
from bson import ObjectId
from loguru import logger
import random


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('took'))
async def took_pill_callback_handler(callback_query: types.CallbackQuery):
    db = SingletonClient.get_data_base()

    split_data = callback_query.data.split(',')
    pill_id = ObjectId(split_data[1])
    t = split_data[2]

    logger.info(f"user_id={callback_query.from_user.id} pill_id={pill_id}")

    pill = await db.Pills.find_one({
        "_id": pill_id
    })

    index = pill.get("time_list").index(t)

    time_status = pill.get("time_status")
    time_status[index] = True

    result = await db.Pills.update_one({
        "_id": pill_id
    },
        {
            "$set": {
                "time_status": time_status
            }
        })
    logger.info(f"user_id={callback_query.from_user.id} pill_id={pill_id} "
                f"update_one result={result.acknowledged} time_status={time_status}")

    good_words = ["You did a great job!", "Awesome!", "Good for you!", "I hope it's because of me."]
    await callback_query.message.reply("I remembered that you took a pill. {}".format(
        good_words[random.randint(0, len(good_words))]))

    await callback_query.message.edit_reply_markup(reply_markup=types.InlineKeyboardMarkup())

    await callback_query.answer()
