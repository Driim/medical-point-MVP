from fastapi import FastAPI

from src.common.context import initialize_context_middleware
from src.common.health_checks import register_health_checks
from src.common.logger import initialize_logger
from src.common.neo4j import initialize_database_middleware
from src.structures.configuration import Configuration
from src.structures.controllers.organization_units import (
    register_organization_units_router,
)


def mock_health_check() -> bool:
    return True


def initialize_application(config: Configuration):
    initialize_logger(config.logging)
    application = FastAPI(
        title="Structures service",
        version="0.1",
    )

    application.state.ROOT_OU = config.root_ou

    health_checks = []

    # Middleware part
    initialize_database_middleware(application, config.neo4j, health_checks)
    initialize_context_middleware(application)

    # Router part
    register_organization_units_router(application, "/v1")

    register_health_checks(application, health_checks)

    return application
