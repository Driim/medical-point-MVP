from fastapi import FastAPI
from src.common.health_checks import register_health_checks
from src.common.logger import initialize_logger
from src.common.context import initialize_context_middleware
from src.common.neo4j import initialize_database_middleware
from src.organizations.configuration import Configuration
from src.organizations.controllers.organizations import register_organizations_router


def mock_health_check() -> bool:
    return True


def initialize_application(config: Configuration):
    initialize_logger(config.logging)
    application = FastAPI(
        title="Organization Units API",
        version="0.1",
    )

    health_checks = []

    # Middleware part
    initialize_database_middleware(application, config.neo4j, health_checks)
    initialize_context_middleware(application)

    # Router part
    # register_campaign_router(application, "/v1")
    register_organizations_router(application, "/v1")

    register_health_checks(application, health_checks)

    return application
