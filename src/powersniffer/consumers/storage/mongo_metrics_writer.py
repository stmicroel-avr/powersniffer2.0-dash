from pymongo import AsyncMongoClient
from pymongo.errors import DuplicateKeyError
from pymongo.asynchronous.database import AsyncDatabase

from powersniffer.config import MongoConfig
from powersniffer.consumers.storage.measurement_value_converter import MeasurementValueConverter
from powersniffer.logger import get_app_logger
from powersniffer.models.measurement import Measurement


class MongoMetricsWriter:
    def __init__(self, config: MongoConfig):
        self.db = None
        self.client = None
        self.config = config
        self.collections = {}
        self.logger = get_app_logger(__name__)

    def _get_collection_name(self, measurement: Measurement):
        """
        Get measurement collection name
        :param measurement: Measurement data
        :return:
        """
        return f'measurements_{measurement.unit.lower()}'

    async def init(self):
        """
        Register client and connect to MongoDB
        :return:
        """
        self.client = AsyncMongoClient(
            host="localhost",
            port=27017,
            username=self.config.username,
            password=self.config.password,
            minPoolSize=1,
            authSource=self.config.dbname,
        )

        db = AsyncDatabase(self.client, self.config.dbname)
        await db.command('ping')
        self.db = db

    async def write_metric(self, metric: Measurement) -> bool:
        """
        Write metric to MongoDB
        :param metric: Metric data
        :return:
        """
        if self.db is None:
            self.logger.error('MongoDB not connected')
            return False

        collection_name = self._get_collection_name(metric)

        if collection_name not in self.collections:
            try:
                collection = self.db[collection_name]
                await collection.create_index("timestamp")
                await collection.create_index("key", unique=True)
            except Exception as e:
                self.logger.error(f"Failed to prepare collection {e}")
                return False

            self.collections[collection_name] = collection

        try:
            await self.collections[collection_name].insert_one({
                'timestamp': metric.timestamp,
                'key': metric.key,
                'value': MeasurementValueConverter(metric).resolve_value(),
            })
        except DuplicateKeyError as e:
            self.logger.debug(f'Duplicate key {e}')
            return True
        except Exception as e:
            self.logger.error(f'Unknown error {e}')
            return False

        return True