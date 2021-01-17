from bot import dp, types


@dp.message_handler(commands=['pills'])
async def pills_list(message: types.Message):
    """
    Send listable list with pills
    :param message:
    :return:
    """
    pass
