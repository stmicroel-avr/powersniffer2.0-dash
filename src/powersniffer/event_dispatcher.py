import logging

from powersniffer.queue_client import QueueClient
from powersniffer.packet_parser import PacketParser
from powersniffer.protocols import JsonSerializableEvent


class EventDispatcher:
    def __init__(self, header: bytes, queue_client: QueueClient) -> None:
        self.parser = PacketParser(header)
        self.queue = queue_client
        self.logger = logging.getLogger(__name__)

    def publish(self, payload: JsonSerializableEvent):
        pass

    async def dispatch(self, ch, packet) -> None:
        """
        Handle all notifications
        :return:
        """
        try:
            series = self.parser.extract(packet)
        except ValueError:
            self.logger.warning("Invalid packet received")
            return

        for event in series:
            await self.queue.publish(event.to_json())

