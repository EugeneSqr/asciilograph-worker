import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

import aio_pika
from aio_pika.pool import Pool
from aio_pika.abc import (
    AbstractConnection,
    AbstractChannel,
    AbstractQueue,
    AbstractIncomingMessage,
)

from settings import get_settings
from logger import set_correlation_id

async def _get_connection() -> AbstractConnection:
    connection_string = (f"amqp://{get_settings().rabbitmq_user}:"
                         f"{get_settings().rabbitmq_password}@"
                         f"{get_settings().rabbitmq_host}/")
    while True:
        try:
            return await aio_pika.connect(connection_string, timeout=get_settings().timeout_seconds)
        except aio_pika.exceptions.AMQPConnectionError:
            logging.info(f"couldn't connect to {get_settings().rabbitmq_host}, retrying...")
            await asyncio.sleep(2)

_connection_pool: Pool[AbstractConnection] = Pool(
    _get_connection,
    max_size=get_settings().rabbitmq_connection_pool_size,
)

@asynccontextmanager
async def get_channel() -> AsyncIterator[AbstractChannel]:
    async with _connection_pool.acquire() as connection:
        yield await connection.channel()

async def image_processing_messages(
    channel: AbstractChannel,
) -> AsyncIterator[AbstractIncomingMessage]:
    queue = await _get_image_processing_queue(channel)
    async with queue.iterator() as messages:
        async for message in messages:
            set_correlation_id(message.correlation_id)
            logging.info(f"got message {message} from message processing queue")
            yield message
            logging.info("message processed")

async def return_processed_image(
    channel: AbstractChannel,
    processed_image: str,
    correlation_id: str | None,
    callback_queue: str | None,
) -> None:
    assert callback_queue is not None
    await channel.default_exchange.publish(
        aio_pika.Message(
            body=processed_image.encode(),
            correlation_id=correlation_id,
        ),
        routing_key=callback_queue,
    )

async def _get_image_processing_queue(channel: AbstractChannel) -> AbstractQueue:
    return await channel.declare_queue(get_settings().rabbitmq_image_processing_queue,
                                       timeout=get_settings().timeout_seconds)
