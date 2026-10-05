import sys
import fcntl
import signal
import asyncio
import logging
from contextlib import contextmanager

from powersniffer.config import load_config, Config
from powersniffer.bluetooth.client import Client
from powersniffer.queue_client import QueueClient
from powersniffer.event_dispatcher import EventDispatcher

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

def soft_stop(sig, frame):
    """
    Handler for the SIGINT/SIGTERM signal.

    :param sig:
    :param frame:
    :return:
    """
    logger.info("Soft stop app signal processing..")
    sys.exit(0)

async def run_async(config: Config) -> None:
    queue_client = QueueClient(config.rmq)
    await queue_client.start()
    bt = Client(
        config.device,
        EventDispatcher(config.device.packet_header, queue_client)
    )

    await bt.run()

def entry() -> None:
    """
    Entry point for the application.
    Run via uv run

    :return:
    """
    configure_logging()
    signal.signal(signal.SIGINT, soft_stop)
    signal.signal(signal.SIGTERM, soft_stop)

    logger.info("Start app..")
    with acquire_bluetooth_lock():
        logger.info("Starting listener")
        config = load_config()
        logger.info(f"Scan all Bluetooth devices and search {config.device.name} with address: {config.device.addr}")
        asyncio.run(run_async(config))
