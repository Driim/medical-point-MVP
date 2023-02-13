# import uptrace
from fastapi import FastAPI

from src.common.context import initialize_context_middleware
from src.common.health_checks import register_health_checks
from src.common.logger import initialize_logger
from src.common.neo4j import initialize_database_middleware
from src.structures.configuration import Configuration
from src.structures.controllers.devices import register_devices_router
from src.structures.controllers.organization_units import (
    register_organization_units_router,
)
from src.structures.controllers.outlets import register_outlets_router
from src.structures.controllers.users import register_users_router
from src.structures.controllers.workers import register_workers_router

# from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


def mock_health_check() -> bool:
    return True


def initialize_application(config: Configuration) -> FastAPI:
    initialize_logger(config.logging)
    application = FastAPI(
        title="Structures service",
        version="0.1",
    )

    # uptrace.configure_opentelemetry(
    #     # Copy DSN here or use UPTRACE_DSN env var.
    #     dsn=config.uptrace_dsn,
    #     service_name="Org Structures",
    #     service_version="1.0.0",
    # )

    # FastAPIInstrumentor.instrument_app(application)

    application.state.ROOT_OU = config.root_ou

    health_checks = []

    # Middleware part
    initialize_database_middleware(application, config.neo4j, health_checks)
    initialize_context_middleware(application)

    # Router part
    register_organization_units_router(application, "")
    register_outlets_router(application, "")
    register_devices_router(application, "")
    register_workers_router(application, "")
    register_users_router(application, "")

    register_health_checks(application, health_checks)

    return application
