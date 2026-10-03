import fcntl
import asyncio
import logging
from contextlib import contextmanager
from powersniffer.config import load_config
from powersniffer.bluetooth.client import Client
from powersniffer.notification_dispatcher import NotificationDispatcher

logger = logging.getLogger(__name__)

def configure_logging() -> None:
    """
    Configure logging for the application.
    :return:
    """
    logging.basicConfig(
        level=logging.INFO,
        format="[%(process)d] [%(levelname)s] %(asctime)s - %(message)s"
    )

@contextmanager
def acquire_bluetooth_lock():
    """
    Acquire an exclusive flock-based lock for Bluetooth access.

    Concurrent access to the Bluetooth host is impossible. Blocks until the lock becomes available.
    Used during deployment of a new release, before the old instance is stopped.
    """
    with open("/tmp/bluetooth.lock", "a") as f:
        logger.info("Acquiring lock...")
        fcntl.flock(f, fcntl.LOCK_EX)
        logger.info("Lock acquired")

        try:
            yield
        finally:
            logger.info("Releasing lock...")
            fcntl.flock(f, fcntl.LOCK_UN)

def entry() -> None:
    """
    Entry point for the application.
    Run via uv
    :return:
    """
    logger.info("Start app..")
    configure_logging()
    with acquire_bluetooth_lock():
        logger.info("Starting listener")
        config = load_config()
        logger.info(f"Scan all Bluetooth devices and search {config.device.name} with address: {config.device.addr}")
        bt = Client(config.device, NotificationDispatcher(header=config.device.packet_header))
        asyncio.run(bt.run())
