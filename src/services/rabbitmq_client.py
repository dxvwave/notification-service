import json
import logging
from typing import Callable, Awaitable

import aio_pika
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from core.config import settings

logger = logging.getLogger(__name__)

MessageHandler = Callable[[str, dict], Awaitable[None]]


class RabbitMQClient:
    def __init__(self, amqp_url: str):
        self.amqp_url = amqp_url
        self.connection = None
        self.channel = None
        self.exchange = None
        self.queue = None
        self._handler: MessageHandler | None = None

    def set_handler(self, handler: MessageHandler) -> None:
        """Register an async callback invoked for every incoming message."""
        self._handler = handler

    @retry(
        stop=stop_after_attempt(15),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(
            (ConnectionError, aio_pika.exceptions.AMQPConnectionError)
        ),
    )
    async def connect(self):
        """Establish a robust connection to the RabbitMQ broker."""
        self.connection = await aio_pika.connect_robust(self.amqp_url)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=10)
        logger.info("Connected to RabbitMQ")

    async def setup_topology(
        self,
        exchange_name: str,
        queue_name: str,
        routing_keys: list[str],
    ):
        """Declare a TOPIC exchange, a durable queue, and bind routing keys."""
        # Must match the exchange type declared by product-service (TOPIC).
        self.exchange = await self.channel.declare_exchange(
            exchange_name,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )

        self.queue = await self.channel.declare_queue(queue_name, durable=True)

        for key in routing_keys:
            await self.queue.bind(self.exchange, routing_key=key)

        logger.info(
            f"Topology ready: exchange={exchange_name}, queue={queue_name}, "
            f"routing_keys={routing_keys}"
        )

    async def consume(self):
        """Start consuming messages and dispatch to the registered handler."""
        if not self.queue:
            raise RuntimeError("Queue is not initialized. Call setup_topology first.")

        async with self.queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process(ignore_processed=True):
                    routing_key = message.routing_key
                    payload = json.loads(message.body)
                    logger.info(f"Received: routing_key={routing_key} payload={payload}")

                    if self._handler:
                        try:
                            await self._handler(routing_key, payload)
                            await message.ack()
                        except Exception:
                            logger.exception(f"Error handling message: routing_key={routing_key}")
                            await message.nack(requeue=False)

    async def close(self):
        """Gracefully close the RabbitMQ connection."""
        if self.connection:
            await self.connection.close()
            logger.info("RabbitMQ connection closed")


rabbit_client = RabbitMQClient(amqp_url=settings.rabbitmq_url)
