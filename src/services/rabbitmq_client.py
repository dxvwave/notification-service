import asyncio
import json
import aio_pika
from typing import Callable, Any, Dict
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from core.config import settings


class RabbitMQClient:
    def __init__(self, amqp_url: str):
        self.amqp_url = amqp_url
        self.connection = None
        self.channel = None
        self.exchange = None
        self.queue = None

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
        # Set QoS to ensure the worker doesn't get overwhelmed
        await self.channel.set_qos(prefetch_count=10)

    async def setup_topology(
        self,
        exchange_name: str,
        queue_name: str,
        routing_keys: list,
    ):
        """Declare exchange, queue and bind them together."""
        # Declare the exchange (Direct type for specific routing)
        self.exchange = await self.channel.declare_exchange(
            exchange_name,
            aio_pika.ExchangeType.DIRECT,
            durable=True,
        )

        # Declare a durable queue for the service
        self.queue = await self.channel.declare_queue(queue_name, durable=True)

        # Bind the queue to multiple routing keys
        for key in routing_keys:
            await self.queue.bind(self.exchange, routing_key=key)

    async def consume(self):
        """Start an infinite loop to consume and process messages."""
        if not self.queue:
            raise RuntimeError("Queue is not initialized. Call setup_topology first.")

        async with self.queue.iterator() as queue_iter:
            async for message in queue_iter:
                # message.process() acts as a context manager:
                # it automatically sends ACK on success or NACK on failure
                async with message.process():
                    routing_key = message.routing_key
                    payload = json.loads(message.body)

                    # Delegate business logic
                    print(f"Received message with routing key: {routing_key}, payload: {payload}")

    async def close(self):
        """Gracefully close the RabbitMQ connection."""
        if self.connection:
            await self.connection.close()


rabbit_client = RabbitMQClient(amqp_url=settings.rabbitmq_url)
