from powersniffer.config import load_config
from powersniffer.logger import get_app_logger
from powersniffer.queue_client import QueueClient

logger = get_app_logger(__name__)

async def run_async(qclient: QueueClient) -> None:
    """
    All async task running.

   :param qclient: RMQ client
   :return: None
    """
    await qclient.start()

def run() -> None:
    """
    Entry point for the application.
    Run via uv run

    :return:
    """
    logger.info("Start queue mongo consumer..")
    config = load_config()
    qclient = QueueClient(config.rmq)
