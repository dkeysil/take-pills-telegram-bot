import motor.motor_asyncio as m_m_a
import os


class SingletonClient:
    client = None
    db = None

    @staticmethod
    def get_client():
        if SingletonClient.client is None:
            MONGODB_USERNAME = os.environ['MONGODB_USERNAME']
            MONGODB_PASSWORD = os.environ['MONGODB_PASSWORD']
            MONGODB_HOSTNAME = os.environ['MONGODB_HOSTNAME']
            MONGODB_PORT = os.environ['MONGODB_PORT']

            SingletonClient.client = m_m_a.AsyncIOMotorClient("mongodb://{}:{}@{}:{}".format(
                MONGODB_USERNAME, MONGODB_PASSWORD, MONGODB_HOSTNAME, str(MONGODB_PORT)))

        return SingletonClient.client

    @staticmethod
    def get_data_base():
        if SingletonClient.db is None:
            client = SingletonClient.get_client()
            MONGODB_DATABASE = os.environ['MONGODB_DATABASE']
            SingletonClient.db = client[MONGODB_DATABASE]

        return SingletonClient.db
