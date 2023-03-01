# flake8: noqa: S311
import logging
import random

from aiokafka import AIOKafkaProducer
from fastapi import Depends
from starlette.requests import Request

from src.common.context.context import get_request
from src.common.kafka.middleware import get_kafka_producer
from src.inspections.domain.inspections.models import Event

logger = logging.getLogger(__name__)


class EventProducerKafka:
    def __init__(
        self,
        producer: AIOKafkaProducer = Depends(get_kafka_producer),
        request: Request = Depends(get_request),
    ):
        self._producer = producer
        self._request = request

    async def produce(self, events: list[Event]):
        topic = self._request.app.state.KAFKA_TOPIC
        logger.debug(f"Sending {len(events)} to kafka topic: {topic}")

        partitions = await self._producer.partitions_for(topic)

        batch = self._producer.create_batch()

        for event in events:
            metadata = batch.append(
                key=None, timestamp=None, value=event.json().encode("utf-8")
            )
            if metadata is None:
                partition = random.choice(tuple(partitions))
                await self._producer.send_batch(batch, topic, partition=partition)
                batch = self._producer.create_batch()
                continue

        partition = random.choice(tuple(partitions))
        await self._producer.send_batch(batch, topic, partition=partition)

        logger.debug("All events are sent")
