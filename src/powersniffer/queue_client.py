import json

import aio_pika
from collections.abc import Callable, Awaitable

from powersniffer.config import RMQConfig


class QueueClient:
    def __init__(self, config: RMQConfig) -> None:
        self.config = config
        self.channel = None
        self.exchange = None
        self.failed_exchange = None
        self.connection = None
        self.queues = {}

    async def _declare_and_bind_queue(self, queue_name: str, failed_exchange_name: str) -> None:
        """
        Declare and bind a queue
        :param queue_name: Name of RMQ queue
        :return: None
        """
        queue = await self.channel.declare_queue(
            queue_name,
            durable=True,
            arguments={"x-dead-letter-exchange": failed_exchange_name},
        )

        await queue.bind(self.exchange)
        self.queues[queue_name] = queue

    async def _declare_failed_queue(self, queue_name: str) -> None:
        """
        Declare and bind a failed queue
        :param queue_name: queue name for failed events
        :return: None
        """
        queue = await self.channel.declare_queue(queue_name, durable=True)
        await queue.bind(self.failed_exchange)

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
        self.exchange = await self.channel.declare_exchange(
            self.config.exchange,
            aio_pika.ExchangeType.FANOUT,
            durable=True
        )

        self.failed_exchange = await self.channel.declare_exchange(
            self.config.failed_exchange,
            aio_pika.ExchangeType.FANOUT,
            durable=True
        )

        await self._declare_failed_queue(self.config.failed_queue)
        await self._declare_and_bind_queue(self.config.q_mongo, self.config.failed_exchange)

    async def stop(self) -> None:
        """
        Stop the rmq client
        :return: None
        """
        if self.connection is not None:
            await self.connection.close()

    async def publish(self, message: str) -> None:
        """
        Publish a message

        :param message:
        :return: None
        """
        if self.connection:
            raw_msg = aio_pika.Message(body=message.encode(), delivery_mode=aio_pika.DeliveryMode.PERSISTENT)
            await self.exchange.publish(raw_msg, routing_key='')
        else:
            with open("./fallback.log", "a", encoding="utf-8") as file:
                file.write(message + "\n")

    async def register_consumer(self, queue: str, callback: Callable[[dict], Awaitable[bool]], prefetch: int = 1) -> None:
        """
        Register a new consumer

        :param queue: Name of RMQ queue
        :param callback: Callback func for new message
        :param prefetch: Prefetch count for new message
        :return: None
        """
        if queue not in self.queues:
            raise RuntimeError(f"Queue {queue} not registered")

        async def on_message(msg: aio_pika.abc.AbstractIncomingMessage) -> None:
            """
            Wrapper for incoming message with auto ack

            :param msg: aio_pika.abc.AbstractIncomingMessage
            :return: None
            """
            try:
                result = await callback(json.loads(msg.body))
            except Exception as e:
                with open("./consumer_error.log", "a", encoding="utf-8") as file:
                    file.write(str(e) + "\n")

                return await msg.reject()

            if result:
                return await msg.ack()

            return await msg.reject(requeue=True)

        await self.channel.set_qos(prefetch_count=prefetch)
        await self.queues[queue].consume(on_message)