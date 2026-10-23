import asyncio
from pydantic import TypeAdapter, ValidationError

from powersniffer.logger import get_app_logger
from powersniffer.models.measurement import Measurement
from powersniffer.consumers.storage.mongo_metrics_writer import MongoMetricsWriter


class MongoEventHandler:
    def __init__(self, storage_writer: MongoMetricsWriter):
        self.storage_writer = storage_writer
        self.logger = get_app_logger(__name__)
        self.event_adapter = TypeAdapter(Measurement)

    async def handle(self, raw_event: dict) -> None:
        try:
            measurement = self.event_adapter.validate_python(raw_event)
        except ValidationError as e:
            self.logger.error(e)
            return

        self.logger.info(measurement)
        await asyncio.sleep(1)