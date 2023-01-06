from fastapi import FastAPI

from .configuration import Neo4JConfiguration
from .decorator import Transactional  # noqa
from .middleware import (  # noqa
    Neo4JSessionMiddleware,
    check_database_connection,
    get_session,
)
from .router import TransactionalRouter, get_transaction  # noqa


def initialize_database_middleware(
    application: FastAPI,
    config: Neo4JConfiguration,
    health_checks: list,
) -> None:
    application.add_middleware(Neo4JSessionMiddleware, config=config)
    # setting default Router
    application.router.route_class = TransactionalRouter
    health_checks.append(check_database_connection)
