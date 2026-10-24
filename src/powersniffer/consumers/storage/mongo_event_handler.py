import time
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
        self._stats = {
            'processed': 0,
            'failed': 0,
        }

    async def handle(self, raw_event: dict) -> bool:
        """
        Handle event received from RabbitMQ
        :param raw_event: Payload of event from queue RabbitMQ
        :return:
        """
        try:
            measurement = self.event_adapter.validate_python(raw_event)
        except ValidationError as e:
            self.logger.error(e)
            return True

        self.logger.debug(
            "Measurement received: key=%s timestamp=%s value=%s unit=%s",
            measurement.key,
            measurement.timestamp,
            measurement.value,
            measurement.unit,
        )

        is_processed =  await self.storage_writer.write_metric(measurement)
        if is_processed:
            self._inc_processed()
        else:
            self._inc_failed()

        return is_processed

    def _inc_failed(self):
        """
        Increment failed counter
        :return:
        """
        self._stats['failed'] += 1

    def _inc_processed(self):
        """
        Increment processed counter
        :return:
        """
        self._stats['processed'] += 1

    async def run_loop_log_stats(self):
        """
        Log cycle stats
        :return:
        """
        while True:
            previous = self._stats.copy()
            tstart = time.monotonic()
            await asyncio.sleep(10)
            period_sec = time.monotonic() - tstart
            failed_average_per_sec = (self._stats['failed'] - previous['failed']) / period_sec
            processed_average_per_sec = (self._stats['processed'] - previous['processed']) / period_sec
            self.logger.info(f"Processed events: {processed_average_per_sec}/s, Failed: {failed_average_per_sec}/s")



