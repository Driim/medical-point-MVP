import logging

from fastapi import Depends
from neo4j import AsyncGraphDatabase, AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.common.context import get_request_context
from .configuration import Neo4JConfiguration

logger = logging.getLogger(__name__)


# Why middleware?
# If we use Depends yield will return after response is send
class Neo4JSessionMiddleware(BaseHTTPMiddleware):
    KEY = "neo4j_session"

    def __init__(self, config: Neo4JConfiguration, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._driver = AsyncGraphDatabase.driver(
            config.uri,
            auth=(config.user, config.password),
        )

    async def dispatch(
        self,
        request: Request,
        next: RequestResponseEndpoint,
    ) -> Response:
        # access_mode = "READ" if transactional is False else "WRITE"
        session = self._driver.session()
        context = get_request_context()
        context[self.KEY] = session

        try:
            response = await next(request)
        finally:
            del context[self.KEY]
            await session.close()

        return response


def get_session() -> AsyncSession:
    context = get_request_context()
    # we want to raise error if KEY not in context
    return context[Neo4JSessionMiddleware.KEY]


async def check_database_connection(
    session: AsyncSession = Depends(get_session),
) -> bool:
    try:
        await session.run("RETURN 1")
        return True
    except:  # noqa
        logger.error("READINESS: database connection")
        return False
