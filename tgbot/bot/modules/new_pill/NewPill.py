from bot import dp, types


@dp.message_handler(commands=['/new'])
async def new_pill(message: types.Message):
    """
    Creates new pill for user
    :param message:
    :return:
    """
    pass
