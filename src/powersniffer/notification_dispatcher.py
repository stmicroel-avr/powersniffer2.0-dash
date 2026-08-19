import logging

from powersniffer.packet_parser import PacketParser


class NotificationDispatcher:
    def __init__(self, header: bytes, *args):
        self.handlers = args
        self.parser = PacketParser(header)
        self.logger = logging.getLogger(__name__)

    def handle(self, ch, packet) -> None:
        """
        Handle all notifications
        :return:
        """
        try:
            series = self.parser.parse(packet)
        except ValueError:
            self.logger.warning("Invalid packet received")
            return

        if not len(self.handlers):
            self.logger.warning(f"No handlers found")
            return

        for handler in self.handlers:
            handler.handle(series)
