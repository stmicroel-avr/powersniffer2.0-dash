import logging

from powersniffer.queue_client import QueueClient
from powersniffer.collector.parser import PacketParser


class EventDispatcher:
    def __init__(self, header: bytes, queue_client: QueueClient) -> None:
        self.parser = PacketParser(header)
        self.queue = queue_client
        self.logger = logging.getLogger(__name__)

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

