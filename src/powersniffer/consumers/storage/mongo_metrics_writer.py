from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from powersniffer.config import MongoConfig
from powersniffer.models.measurement import Measurement


class MongoMetricsWriter:
    def __init__(self, config: MongoConfig):
        self.db = None
        self.client = None
        self.config = config

    def connect(self):
        self.client = AsyncMongoClient(username=self.config.username, password=self.config.password)
        self.db = AsyncDatabase(self.client, self.config.dbname)

    async def write(self, metric: Measurement):
        if self.db is None:
            self.connect()

        await self.db.insert_one(metric)