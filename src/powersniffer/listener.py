import asyncio
import logging
from powersniffer.config import load_config
from powersniffer.bluetooth.client import Client
logger = logging.getLogger(__name__)

def configure_logging() -> None:
    """
    Configure logging for the application.
    :return:
    """
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(asctime)s - %(message)s"
    )

def entry() -> None:
    """
    Entry point for the application.
    Run via uv
    :return:
    """
    configure_logging()
    logger.info("Starting listener")
    config = load_config()
    logger.info(f"Config: {config.device.uid}")
    bt = Client(config.device)
    asyncio.run(bt.scan())