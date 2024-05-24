import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


class MongoDBConnection:
    def __init__(self, connection_string=os.environ.get("MONGODB_URI")):
        self.client = MongoClient(connection_string)
        self.db = self.client[os.environ.get("MONGODB_DB_NAME")]

    @property
    def database(self):
        return self.db
