from random import seed

from fastapi import FastAPI

from src.common.context import initialize_context_middleware
from src.common.health_checks import register_health_checks
from src.common.logger import initialize_logger
from src.inspections.configuration import Configuration
from src.inspections.controllers.inspections import register_inspections_router


def initialize_application(config: Configuration) -> FastAPI:
    initialize_logger(config.logging)

    seed()

    application = FastAPI(
        title="Inspections generator service",
        version="0.1",
    )

    application.state.STRUCTURES_URL = config.structures_url

    initialize_context_middleware(application)

    health_checks = []

    register_inspections_router(application, "/v1")

    register_health_checks(application, health_checks)

    return application
