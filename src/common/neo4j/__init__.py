from .configuration import Neo4JConfiguration
from .middleware import Neo4JSessionMiddleware, get_session, check_database_connection
from .decorator import Transactional
from .router import TransactionalRouter

from fastapi import FastAPI


def initialize_database_middleware(
    application: FastAPI,
    config: Neo4JConfiguration,
    health_checks: list,
) -> None:
    application.add_middleware(Neo4JSessionMiddleware, config=config)
    # setting default Router
    application.router.route_class = TransactionalRouter
    health_checks.append(check_database_connection)
