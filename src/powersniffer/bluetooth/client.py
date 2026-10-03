import asyncio
import logging
from asyncio import CancelledError

from powersniffer.config import DeviceConfig
import powersniffer.bluetooth.exceptions as BTExceptions
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
        try:
            while True:
                try:
                    self.logger.info(f"Rediscover device with addr {self.device_config.addr}")
                    device = await self.discover(self.device_config.addr)
                    self.logger.info(f"Device {self.device_config.addr} found")
                    await self.reconnect(device)
                except (BTExceptions.NotifyCharacteristicNotFoundError,
                        BTExceptions.ConnectionAttemptsExceededError,
                        BTExceptions.NotificationSubscriptionError):
                    continue
                except Exception as e:
                    self.logger.exception(e)
                    await asyncio.sleep(5)
        except CancelledError:
            return

    async def discover(self, addr: str) -> BLEDevice:
        """
        Try to discover device with addr

        :param addr: BLE device addr
        :return: BLEDevice
        """
        attempts = 0
        while True:
            found_device = None
            try:
                found_device = await BleakScanner.find_device_by_address(addr)
            except BleakError as e:
                self.logger.debug(f"Error search device: {e}")

            if found_device is not None:
                break

            attempts += 1
            self.logger.warning("Device %s not found(%s). Wait 10 seconds and retry..", addr, attempts)
            await asyncio.sleep(10)

        return found_device

    async def reconnect(self, device: BLEDevice|str):
        """
        Connect to a device with retry
        :param device: Device to connect with
        :return:
        """
        disconnection_event = asyncio.Event()
        client = BleakClient(
            address_or_ble_device=device,
            disconnected_callback=lambda _: disconnection_event.set(),
        )

        try:
            attempts = 1
            while not await self.connect(client):
                if attempts >= 5:
                    self.logger.warning("Connection attempts exceeded")
                    raise BTExceptions.ConnectionAttemptsExceededError()

                self.logger.info("Device is not connected(%s). Wait 5 second and retry connect...", attempts)
                attempts += 1
                await asyncio.sleep(5)
                disconnection_event.clear()

            notify_specifier = await self.get_notify_char_specifier(client)
            if not notify_specifier:
                self.logger.warning(f"Unable to find characteristic type notify")
                raise BTExceptions.NotifyCharacteristicNotFoundError

            try:
                await client.start_notify(notify_specifier, self.notification_dispatcher.handle)
            except BleakError as e:
                self.logger.debug(f"Failed to start notify: {e}")
                self.logger.warning(f"Notify subscription error")
                raise BTExceptions.NotificationSubscriptionError()

            await disconnection_event.wait()
        finally:
            if client and client.is_connected:
                try:
                    await client.disconnect()
                except Exception as e:
                    self.logger.warning(f"Failed to disconnect {client.address}")


    async def connect(self, client: BleakClient) -> bool:
        """
        Connect to Bluetooth device

        :param client:
        :return:
        """

        self.logger.info(f"Connecting to {client.address}")

        try:
            await client.connect()
        except BleakError as e:
            self.logger.warning(f"Failed to connect {client.address}. {e}")
            return False
        except TimeoutError as e:
            self.logger.warning(f"Timeout to connect {client.address}. {e}")
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

