from bot import dp, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from loguru import logger
from aiogram.dispatcher import FSMContext
from datetime import time
from motor_client import SingletonClient
from bot.modules.start.Start import start


class NewPill(StatesGroup):
    title = State()
    add_time = State()


@dp.message_handler(commands=['new'])
async def new_pill(message: types.Message):
    """
    Creates new pill for user
    :param message:
    :return:
    """
    logger.info(f"/new pill user_id={message.from_user.id}")
    db = SingletonClient.get_data_base()
    user = await db.Users.find_one({
        "telegram_id": message.from_user.id
    })
    if not user:
        await start(message)

    await message.answer("Please, send me pill title.\nIf you want to cancel this operation type /cancel.")
    await NewPill.title.set()


@dp.message_handler(state=NewPill.title)
async def set_pill_title(message: types.Message, state: FSMContext):
    logger.info(f"user_id={message.from_user.id}")
    await state.update_data(title=message.text)

    await message.answer("Send me the time of the next pill intake (like that <code>15:30</code>)."
                         "\nAfter that you can add some more.")
    await NewPill.add_time.set()


@dp.message_handler(state=NewPill.add_time)
async def set_time(message: types.Message, state: FSMContext):
    logger.info(f"user_id={message.from_user.id}")
    try:
        pill_time: time = time.fromisoformat(message.text)
    except ValueError:
        return await message.answer("Sorry, incorrect.\nRight format of time is <code>HH:MM</code>")

    pill_time_list = await state.get_data()
    pill_time_list = pill_time_list.get("pill_time_list")

    if not pill_time_list:
        pill_time_list = []

    text = ''
    if pill_time.strftime("%H:%M") in pill_time_list:
        text += '<b>Sorry, this time already in list.</b>\n\n'
    else:
        pill_time_list.append(pill_time.strftime("%H:%M"))
    pill_time_list.sort()
    await state.update_data(pill_time_list=pill_time_list)

    if len(pill_time_list) > 40:
        return message.answer("This is already too much.\nPlease save.")

    markup = pills_time_list_markup(pill_time_list)

    text += "Add more time for notifications or save this list." \
            "\n<b>Press on time</b> if you want to delete it." \
            "\nIf you want to cancel this operation type /cancel."

    await message.answer(text, reply_markup=markup)


def pills_time_list_markup(pill_time_list: list) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()

    lst = []
    for i, pill_time in enumerate(pill_time_list):
        if i % 5 == 0:
            lst.append([types.InlineKeyboardButton(text=pill_time,
                                                   callback_data=f"delete-pill-time,{pill_time}")])
        else:
            lst[i // 5].append(
                types.InlineKeyboardButton(text=pill_time,
                                           callback_data=f"delete-pill-time,{pill_time}"))
    for row in lst:
        markup.row(*row)

    one_more_pill_time_button = types.InlineKeyboardButton(text="Add one more time",
                                                           callback_data="add-pill-time")
    save_time_button = types.InlineKeyboardButton(text="Save",
                                                  callback_data="save-pill-time")
    markup.row(one_more_pill_time_button, save_time_button)

    return markup


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('add-pill-time'),
                           state=NewPill.add_time)
async def set_more_pill(callback_query: types.CallbackQuery, state: FSMContext):
    logger.info(f"user_id={callback_query.from_user.id}")
    await callback_query.message.answer("Send me the time of the next pill intake (like that <code>15:30</code>)."
                                        "\nAfter that you can add some more.")
    await callback_query.answer()


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('delete-pill-time'),
                           state=NewPill.add_time)
async def delete_pill(callback_query: types.CallbackQuery, state: FSMContext):
    logger.info(f"user_id={callback_query.from_user.id}")
    pill_time = callback_query.data.split(',')[1]

    pill_time_list = await state.get_data()
    pill_time_list = pill_time_list.get("pill_time_list")
    pill_time_list.remove(pill_time)
    await state.update_data(pill_time_list=pill_time_list)

    await callback_query.message.answer("Time {} has been deleted.".format(pill_time))

    text = "Add more time for notifications or save this list." \
           "\n<b>Press on time</b> if you want to delete it." \
           "\nIf you want to cancel this operation type /cancel."
    markup = pills_time_list_markup(pill_time_list)
    await callback_query.message.answer(text, reply_markup=markup)

    await callback_query.answer()


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('save-pill-time'),
                           state=NewPill.add_time)
async def save_pills_time_list(callback_query: types.CallbackQuery, state: FSMContext):
    logger.info(f"user_id={callback_query.from_user.id}")

    _state = await state.get_data()
    title = _state.get("title")
    pill_time_list = _state.get("pill_time_list")

    db = SingletonClient.get_data_base()

    user = await db.Users.find_one({
        "telegram_id": callback_query.from_user.id
    })

    result = await db.Pills.insert_one({
        "title": title,
        "time_list": pill_time_list,
        "time_status": [],
        "user": user.get("_id")
    })
    logger.info(f"save pills user_id={callback_query.from_user.id} "
                f"insert_one result={result.acknowledged} id={result.inserted_id}")

    await callback_query.message.edit_reply_markup(reply_markup=types.InlineKeyboardMarkup())
    await callback_query.message.answer("The pill is successfully saved, wait for reminders.")
    await state.finish()
    await callback_query.answer()
