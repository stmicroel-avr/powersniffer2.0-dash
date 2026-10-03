import asyncio
import logging

from powersniffer.config import DeviceConfig
from bleak import BleakClient, BleakError, BleakScanner, BLEDevice

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
        self.logger.info(f"Discover device with addr {self.device_config.addr}")

        device = await BleakScanner.find_device_by_address(self.device_config.addr)
        if device is None:
            self.logger.warning("Device %s not found", self.device_config.addr)
            await asyncio.sleep(3)
            return

        await self.reconnect(device)

    async def reconnect(self, device: BLEDevice|str):
        """
        Connect to a device with retry
        :param device: Device to connect with
        :return:
        """
        client = BleakClient(
            address_or_ble_device=device,
            timeout=15
        )

        connected = False
        while not connected:
            connected = await self.connect(client)
            if connected:
                break

            await asyncio.sleep(2)

        notify_specifier = await self.get_notify_char_specifier(client)
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

    async def get_notify_char_specifier(self, client: BleakClient):
        """
        Get a character type notify
        :param client:
        :return:
        """
        self.logger.info("Services count: %s", len(client.services.services))

        for service in client.services:
            for characteristic in service.characteristics:
                if 'notify' in characteristic.properties:
                    return characteristic.uuid

        return None

