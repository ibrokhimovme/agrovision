"""
RabbitMQ publisher skeleton.
Publishes domain events to the agrovision.events exchange.
"""
from __future__ import annotations

import json
import logging
from typing import Optional

import aio_pika
from aio_pika import Message, DeliveryMode

from app.core.config import settings
from shared.events.schemas import BaseEvent

logger = logging.getLogger(__name__)


class EventPublisher:
    _connection: Optional[aio_pika.RobustConnection] = None
    _channel: Optional[aio_pika.Channel] = None
    _exchange: Optional[aio_pika.Exchange] = None

    async def connect(self) -> None:
        self._connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        self._channel = await self._connection.channel()
        self._exchange = await self._channel.declare_exchange(
            "agrovision.events",
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )
        logger.info("EventPublisher connected to RabbitMQ")

    async def publish(self, event: BaseEvent) -> None:
        if self._exchange is None:
            raise RuntimeError("EventPublisher not connected. Call connect() first.")
        payload = event.model_dump_json().encode()
        message = Message(
            payload,
            delivery_mode=DeliveryMode.PERSISTENT,
            content_type="application/json",
            headers={"event_type": type(event).__name__},
        )
        await self._exchange.publish(message, routing_key=event.routing_key)
        logger.debug("Published event %s with routing key %s", type(event).__name__, event.routing_key)

    async def close(self) -> None:
        if self._connection:
            await self._connection.close()


publisher = EventPublisher()
