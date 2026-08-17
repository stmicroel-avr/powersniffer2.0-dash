import logging


class PacketParser:
    def __init__(self):
        self.logger: logging.Logger = logging.getLogger(__name__)

    def parse(self, data: bytearray) -> None:
        self.logger.info(f"Received {len(data)} bytes")
        self.logger.info(data)
        pass

