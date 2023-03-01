from random import seed

from fastapi import FastAPI

from src.common.clickhouse.middleware import initialize_database_middleware
from src.common.context import initialize_context_middleware
from src.common.health_checks import register_health_checks
from src.common.kafka import initialize_kafka_middleware
from src.common.logger import initialize_logger
from src.inspections.configuration import Configuration
from src.inspections.controllers.generator import register_generator_router
from src.inspections.controllers.inspections import register_inspections_router


def initialize_application(config: Configuration) -> FastAPI:
    initialize_logger(config.logging)

    seed()

    application = FastAPI(
        title="Inspections generator service",
        version="0.1",
    )

    application.state.KAFKA_TOPIC = config.kafka.topic

    health_checks = []

    application.state.STRUCTURES_URL = config.structures_url

    initialize_kafka_middleware(application, config.kafka)
    initialize_database_middleware(application, config.clickhouse, health_checks)
    initialize_context_middleware(application)

    register_generator_router(application, "/v1")
    register_inspections_router(application, "/v1")

    register_health_checks(application, health_checks)

    return application
