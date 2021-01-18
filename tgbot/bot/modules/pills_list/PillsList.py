from bot import dp, types
from motor_client import SingletonClient
from loguru import logger
from bson import ObjectId


@dp.message_handler(commands=['pills'])
async def pills_list(message: types.Message):
    """
    Send listable list with pills
    :param message:
    :return:
    """
    logger.info(f"/pills user_id={message.from_user.id}")

    db = SingletonClient.get_data_base()
    user = await db.Users.find_one({
        "telegram_id": message.from_user.id
    })

    markup = types.InlineKeyboardMarkup()

    """
    callback_data:
    1) pl - module name
    2) l, r, n - left, right, none
    3) int - page num
    4) user_id
    """
    string = "List of your current pills:"
    markup = get_pills_list_markup(markup, await get_pills(0, user.get("_id")))

    left_button = types.InlineKeyboardButton(
        text='❌', callback_data=f'pl,l,0,{user.get("_id")}')

    right_list = await get_pills(1, user.get("_id"))
    if right_list:
        right_button = types.InlineKeyboardButton(
            text='➡️', callback_data=f'pl,r,1,{user.get("_id")}'
        )

        markup.row(left_button, right_button)

    _message = await message.answer(string, reply_markup=markup)


@dp.callback_query_handler(lambda callback_query: callback_query.data.split(',')[0] == 'pl')
async def handle_pill_arrow_callback_query(callback_query: types.CallbackQuery):
    """
    Handle callback with clicks on left and right buttons
    Args:
        callback_query (types.CallbackQuery):
    """

    split_data = callback_query.data.split(',')
    logger.info(f"user_id={callback_query.from_user.id} data={split_data}")
    if split_data[1] == 'n':
        return await callback_query.answer(text='Nothing more...')

    page = int(split_data[2])
    parameter = split_data[3]

    markup = types.InlineKeyboardMarkup()
    markup = get_pills_list_markup(markup, await get_pills(page, parameter))

    string = "List of your current pills:"

    # Checks pills on previous page.
    left_list = await get_pills(page - 1, parameter)
    if left_list:
        left_button = types.InlineKeyboardButton(
            text='⬅️', callback_data=f'pl,l,{page - 1},{parameter}')
    else:
        left_button = types.InlineKeyboardButton(
            text='❌', callback_data=f'pl,n,{page},{parameter}')

    # Checks pills on next page.
    right_list = await get_pills(page + 1, parameter)
    if right_list:
        right_button = types.InlineKeyboardButton(
            text='➡️', callback_data=f'pl,r,{page + 1},{parameter}')
    else:
        right_button = types.InlineKeyboardButton(
            text='❌', callback_data=f'pl,n,{page},{parameter}')

    markup.row(left_button, right_button)

    _message = await callback_query.message.edit_text(string, reply_markup=markup)
    await callback_query.answer()


@dp.callback_query_handler(lambda callback_query: callback_query.data.split(',')[0] == 'pil' and
                                                  callback_query.data.endswith("delete"))
async def handle_pill_delete_callback_query(callback_query: types.CallbackQuery):
    """
    handle delete pill callback and it from db
    :param callback_query:
    :return:
    """
    logger.info(f"user_id={callback_query.from_user.id} data={callback_query.data}")
    pill_id = ObjectId(callback_query.data.split(',')[1])

    db = SingletonClient.get_data_base()

    result = await db.Pills.delete_many({
        "_id": pill_id
    })
    logger.info(f"delete pill user_id={callback_query.from_user.id} "
                f"delete_one result={result.acknowledged} count={result.deleted_count}")
    await callback_query.message.edit_reply_markup(reply_markup=types.InlineKeyboardMarkup())
    await callback_query.message.answer("The pill was successfully removed..")
    await callback_query.answer()


@dp.callback_query_handler(lambda callback_query: callback_query.data.split(',')[0] == 'pil')
async def handle_pill_callback_query(callback_query: types.CallbackQuery):
    """
    handle pill callback and let user control it
    :param callback_query:
    :return:
    """
    logger.info(f"user_id={callback_query.from_user.id} data={callback_query.data}")
    pill_id = ObjectId(callback_query.data.split(',')[1])

    db = SingletonClient.get_data_base()
    pill = await db.Pills.find_one({
        "_id": pill_id
    })

    string = "Title: {}\n".format(pill.get("title"))

    string += "\nList of times for notifications:"
    for time in pill.get("time_list"):
        string += "\n{}".format(time)

    markup = types.InlineKeyboardMarkup()

    markup.add(types.InlineKeyboardButton("Delete pill", callback_data=f"{callback_query.data},delete"))

    await callback_query.message.edit_text(string, reply_markup=markup)
    await callback_query.answer()


async def get_pills(page: int, parameter: str) -> (list, int):
    """
    Sugar to get pills list
    Args:
        page (int): page num from callback data
        parameter ([type]): user_id to find pills
    Returns:
        list[{'total': int, 'fund': str}]: list of pills for page
    """
    db = SingletonClient.get_data_base()

    pills = db.Pills.find({
        "user": ObjectId(parameter)
    })
    pills = await pills.to_list(length=await db.Pills.count_documents({}))

    size = 10

    try:
        return pills[page * size: page * size + size]
    except IndexError:
        return []


def get_pills_list_markup(markup: types.InlineKeyboardMarkup(), pills: list) -> types.InlineKeyboardMarkup():
    for pill in pills:
        """
        Send inline keyboard
        callback data:
        pil,pill_id
        pil - event list - module name
        pill_id - in string format '5fb05fee9e1ea634f3eecc73'
        """
        callback_data = 'pil,'
        callback_data += str(pill['_id'])

        string = pill['title'][0:15]
        button = types.InlineKeyboardButton(text=string, callback_data=callback_data)
        markup.row(button)
        logger.info(markup)
    return markup
