import logging

from aioarango import ArangoClient
from aioarango.database import StandardDatabase
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.common.arango.configuration import ArangConfiguration
from src.common.context import get_request_context

logger = logging.getLogger(__name__)


class ArangoMiddleware(BaseHTTPMiddleware):
    KEY = "arango_session"

    def __init__(self, config: ArangConfiguration, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.client = ArangoClient(hosts=config.uri)
        self.config = config

    async def dispatch(
            self,
            request: Request,
            call_next: RequestResponseEndpoint,
    ) -> Response:
        database = await self.client.db(self.config.db, username=self.config.user, password=self.config.password)
        context = get_request_context()
        context[self.KEY] = database

        logger.info(database)

        try:
            response = await call_next(request)
        finally:
            del context[self.KEY]

        return response


def get_session() -> StandardDatabase:
    context = get_request_context()
    # we want to raise error if KEY not in context
    return context[ArangoMiddleware.KEY]
