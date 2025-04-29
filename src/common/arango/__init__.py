from fastapi import FastAPI

from src.common.arango.configuration import ArangConfiguration
from src.common.arango.middleware import ArangoMiddleware


def initialize_arango_middleware(
    application: FastAPI,
    config: ArangConfiguration,
    health_checks: list,
) -> None:
    application.add_middleware(ArangoMiddleware, config=config)
    # setting default Router
    # health_checks.append(check_database_connection)
