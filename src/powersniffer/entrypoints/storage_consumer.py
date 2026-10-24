import signal
import asyncio

from powersniffer.consumers.storage.mongo_event_handler import MongoEventHandler
from powersniffer.consumers.storage.mongo_metrics_writer import MongoMetricsWriter
from powersniffer.logger import get_app_logger
from powersniffer.queue_client import QueueClient
from powersniffer.config import load_config, Config

logger = get_app_logger(__name__)
terminate_event = asyncio.Event()

async def start_consumer(config: Config) -> None:
    """
    Start consumer asynchronously

   :param config: RMQConfig∞
   :return: None
    """

    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, lambda: terminate_event.set())
    loop.add_signal_handler(signal.SIGTERM, lambda: terminate_event.set())

    # Connect to mongo
    mongo_writer = MongoMetricsWriter(config.mongo)
    await mongo_writer.init()

    # Initialize event handler
    processor = MongoEventHandler(mongo_writer)

    # Connect to RMQ and start consumer
    client = QueueClient(config.rmq)

    # Stats logger
    log_stats_task = asyncio.create_task(processor.run_loop_log_stats())
    try:
        await client.start()
        await client.register_consumer(config.rmq.q_mongo, processor.handle)
        await terminate_event.wait()
    finally:
        logger.info("Stop consumer asynchronously..")
        await client.stop()
        logger.info("RMQ consumer stopped")
        log_stats_task.cancel()
        logger.info("Event handler stopped")
        await mongo_writer.stop()
        logger.info("Mongo client stopped")

def run() -> None:
    """
    Entry point for the application.
    Run via uv run

    :return:
    """
    logger.info("Start queue mongo consumer..")
    config = load_config()
    asyncio.run(start_consumer(config))