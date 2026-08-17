import asyncio
import logging

from powersniffer.config import DeviceConfig
from bleak import BleakClient, BleakScanner, BLEDevice, BleakError

from powersniffer.notification_dispatcher import NotificationDispatcher


class Client:
    def __init__(self, device_config: DeviceConfig, dispatcher: NotificationDispatcher):
        self.device_config = device_config
        self.logger = logging.getLogger(__name__)
        self.notification_dispatcher = dispatcher

    async def run(self):
        """
        Entry point for running the client

        :return:
        """
        device = await self.scan()
        if not device:
            self.logger.error(f"Target device UID {self.device_config.addr} not found!")
            return

        self.logger.info(f"Target device {device.name} with address {device.address} found")
        await self.reconnect(device)

    async def reconnect(self, device: BLEDevice):
        """
        Connect to a device with retry
        :param device: Device to connect with
        :return:
        """
        client = BleakClient(
            address_or_ble_device=device,
            timeout=10,
        )

        connected = False
        while not connected:
            connected = await self.connect(client)
            if connected:
                break

            await asyncio.sleep(3)

        notify_specifier = self.get_notify_char_specifier(client)
        if not notify_specifier:
            self.logger.warning(f"Unable to find characteristic type notify for device {client.address}")
            return

        await client.start_notify(notify_specifier, self.notification_dispatcher.handle)
        while True:
            await asyncio.sleep(1)

    async def connect(self, client: BleakClient) -> bool:
        """
        Connect to device
        :param client:
        :return:
        """
        self.logger.info(f"Connecting to {client.address}")

        try:
            await client.connect()
        except BleakError as e:
            self.logger.warning(f"Failed to connect to {client.address}. {e}")
            return False

        if not client.is_connected:
            self.logger.warning(f"Unable to connect to {client.address}")
            return False

        self.logger.info(f"Connected to {client.address}")

        return True

    def get_notify_char_specifier(self, client: BleakClient):
        """
        Get a character type notify
        :param client:
        :return:
        """
        for service in client.services:
            for characteristic in service.characteristics:
                if 'notify' in characteristic.properties:
                    return characteristic.uuid
        return None

    async def scan(self) -> BLEDevice | None:
        """
        Scan all available devices
        :return:
        """
        scanner = BleakScanner()
        devices = await scanner.discover()
        for device in devices:
            self.logger.debug(f"Found device: {device}")
            if device.address == self.device_config.addr and device.name == self.device_config.name:
                return device

        return None

