from pydantic import TypeAdapter, ValidationError

from powersniffer.consumers.storage.measurement_value_converter import MeasurementValueConverter
from powersniffer.logger import get_app_logger
from powersniffer.models.measurement import Measurement
from powersniffer.web.websocket import WebSocketPool


class WebSocketEventHandler:
    def __init__(self, pool: WebSocketPool):
        self.pool = pool
        self.logger = get_app_logger(__name__)
        self.event_adapter = TypeAdapter(Measurement)

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
            return False

        self.logger.debug(
            "Measurement received: key=%s timestamp=%s value=%s unit=%s",
            measurement.key,
            measurement.timestamp,
            measurement.value,
            measurement.unit,
        )

        await self.pool.broadcast({
            'unit': measurement.unit,
            'timestamp': measurement.timestamp,
            'key': measurement.key,
            'value': MeasurementValueConverter(measurement).resolve_value(),
        })

        return True

