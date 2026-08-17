from powersniffer.config import DeviceConfig
from bleak import BleakScanner
import logging


class Client:
    def __init__(self, device_config: DeviceConfig):
        self.device_config = device_config

    async def scan(self):
        logger = logging.getLogger(__name__)
        scanner = BleakScanner()
        devices = await scanner.discover()
        for device in devices:
            logger.info(device)

