from contextlib import contextmanager
from contextvars import ContextVar
import logging
from typing import ContextManager, Optional

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

_context: ContextVar[dict]
logger = logging.getLogger(__name__)

REQ = "request"


class AsyncContextMiddleware(BaseHTTPMiddleware):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @contextmanager
    def context_manager(self, initial: Optional[dict] = None) -> ContextManager:
        global _context

        if initial is None:
            initial = {}

        token = _context.set(initial)
        logger.debug(f"{initial} saved in context")
        try:
            yield
        finally:
            logger.debug("Request removed from context")
            _context.reset(token)

    async def dispatch(
        self,
        request: Request,
        next: RequestResponseEndpoint,
    ) -> Response:
        with self.context_manager({REQ: request}):
            return await next(request)


def get_request_context() -> dict:
    global _context
    return _context.get()


def initialize_context_middleware(application: FastAPI) -> None:
    """
    Middlewark creates a special storage for each request
    """

    def init_global_context() -> None:
        global _context
        _context = ContextVar("request_context")
        logger.debug("Global async context initialized")

    application.add_event_handler(event_type="startup", func=init_global_context)
    application.add_middleware(AsyncContextMiddleware)
