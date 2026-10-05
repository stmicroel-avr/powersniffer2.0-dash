import logging
import aio_pika
from aio_pika import ExchangeType, Message

from powersniffer.config import RMQConfig


class QueueClient:
    def __init__(self, config: RMQConfig) -> None:
        self.config = config
        self.channel = None
        self.exchange = None
        self.connection = None
        self.logger = logging.getLogger(__name__)

    async def start(self) -> None:
        """
        Start the rmq client (connect + create channel + declare exchange/queues)

        :return: None
        """
        self.connection = await aio_pika.connect_robust(
            login=self.config.username,
            password=self.config.password,
            virtualhost=self.config.vhost,
        )

        self.channel = await self.connection.channel()

        self.exchange = await self.channel.declare_exchange(self.config.exchange, ExchangeType.FANOUT)
        queue = await self.channel.declare_queue(self.config.q_mongo)
        await queue.bind(self.exchange)

    async def stop(self) -> None:
        """
        Stop the rmq client
        :return:
        """
        if self.connection:
            await self.connection.close()

    async def publish(self, message: str) -> None:
        """
        Publish a message

        :param message:
        :return:
        """
        if self.connection:
            await self.exchange.publish(message)
        else:
            with open("./fallback.log", "a", encoding="utf-8") as file:
                file.write(message + "\n")