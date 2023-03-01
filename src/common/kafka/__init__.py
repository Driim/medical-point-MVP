import asyncio
import logging

from aiokafka import AIOKafkaProducer
from aiokafka.helpers import create_ssl_context
from fastapi import FastAPI

from src.common.kafka.configuration import KafkaConfiguration
from src.common.kafka.middleware import KafkaMiddleware

_producer: AIOKafkaProducer | None = None

logger = logging.getLogger(__name__)


def initialize_kafka_middleware(
    application: FastAPI,
    config: KafkaConfiguration,
) -> None:
    global _producer

    if _producer is None:
        loop = asyncio.get_event_loop()

        context = create_ssl_context(
            cafile=config.cafile,
        )

        _producer = AIOKafkaProducer(
            loop=loop,
            bootstrap_servers=config.instance,
            # acks=0,  # durability doesn't matter now
            request_timeout_ms=300,
            security_protocol="SASL_SSL",
            sasl_mechanism="SCRAM-SHA-512",
            sasl_plain_username=config.username,
            sasl_plain_password=config.password,
            ssl_context=context,
        )

        @application.on_event("startup")
        async def start_producer():
            await _producer.start()

        @application.on_event("shutdown")
        async def stop_producer():
            await _producer.stop()

    application.add_middleware(KafkaMiddleware, producer=_producer)
