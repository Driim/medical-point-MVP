import logging

from aiokafka import AIOKafkaProducer
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from ..context import get_request_context

logger = logging.getLogger(__name__)


class KafkaMiddleware(BaseHTTPMiddleware):
    KEY = "producer"

    def __init__(self, producer: AIOKafkaProducer, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._producer = producer

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        context = get_request_context()
        context[self.KEY] = self._producer

        try:
            logger.info("Inserting kafka producer to context")
            return await call_next(request)
        finally:
            del context[self.KEY]


def get_kafka_producer() -> AIOKafkaProducer:
    context = get_request_context()
    # we want to raise error if KEY not in context
    return context[KafkaMiddleware.KEY]
