import logging

from powersniffer.packet_parser import PacketParser


class NotificationDispatcher:
    def __init__(self, header: bytes):
        self.parser = PacketParser(header)
        self.logger = logging.getLogger(__name__)

    def dispatch(self, ch, packet) -> None:
        """
        Handle all notifications
        :return:
        """
        try:
            series = self.parser.extract(packet)
        except ValueError:
            self.logger.warning("Invalid packet received")
            return

