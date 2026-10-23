from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from powersniffer.config import MongoConfig
from powersniffer.consumers.storage.measurement_value_converter import MeasurementValueConverter
from powersniffer.models.measurement import Measurement


class MongoMetricsWriter:
    def __init__(self, config: MongoConfig):
        self.db = None
        self.client = None
        self.config = config
        self.collections = {}

    def _get_collection_name(self, measurement: Measurement):
        """
        Get measurement collection name
        :param measurement: Measurement data
        :return:
        """
        return f'measurements_{measurement.unit}'

    def connect(self):
        """
        Register client and connect to MongoDB
        :return:
        """
        self.client = AsyncMongoClient(username=self.config.username, password=self.config.password)
        self.db = AsyncDatabase(self.client, self.config.dbname)

    async def write_metric(self, metric: Measurement):
        """
        Write metric to MongoDB
        :param metric: Metric data
        :return:
        """
        if self.db is None:
            self.connect()

        collection_name = self._get_collection_name(metric)

        if collection_name not in self.collections:
            self.collections[collection_name] = await self.db.create_collection(
                collection_name,
                timeseries={"timeField": "timestamp", "metaField": "metadata", "granularity": "seconds"}
            )

        await self.collections[collection_name].insert_one({
            'timestamp': metric.timestamp,
            'key': metric.key,
            'value': MeasurementValueConverter(metric).resolve_value(),
        })