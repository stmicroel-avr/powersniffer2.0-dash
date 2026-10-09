import signal
import asyncio

from powersniffer.config import load_config, RMQConfig
from powersniffer.logger import get_app_logger
from powersniffer.queue_client import QueueClient

logger = get_app_logger(__name__)
terminate_event = asyncio.Event()

async def on_new_event(event: dict) -> bool:
    """
    New event received from RMQ
    :param event: Event
    :return:
    """
    logger.info(f"Event received from RMQ: {event}")
    return True

async def start_consumer(config: RMQConfig) -> None:
    """
    Start consumer asynchronously

   :param config: RMQConfig
   :return: None
    """
    client = QueueClient(config)

    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, lambda: terminate_event.set())
    loop.add_signal_handler(signal.SIGTERM, lambda: terminate_event.set())

    try:
        await client.start()
        await client.register_consumer(config.q_mongo, on_new_event)
        await terminate_event.wait()
    finally:
        logger.info("Stop consumer asynchronously")
        await client.stop()

def run() -> None:
    """
    Entry point for the application.
    Run via uv run

    :return:
    """
    logger.info("Start queue mongo consumer..")
    config = load_config()
    asyncio.run(start_consumer(config.rmq))