import logging
from asyncio import current_task

from fastapi import Depends, FastAPI, status
from sqlalchemy import orm
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    create_async_engine,
)
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.common.context import get_request_context

from .configuration import ClickhouseConfiguration

logger = logging.getLogger(__name__)


# Why middleware?
# If we use "Depend" yield will return after response is sent
class DatabaseSessionMiddleware(BaseHTTPMiddleware):
    KEY = "session"

    def __init__(self, config: ClickhouseConfiguration, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._engine = create_async_engine(
            config.url,
            echo=config.echo,
            echo_pool=config.echo,
            future=True,
            pool_size=config.pool_size,
        )
        self._session_factory = async_scoped_session(
            orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
                expire_on_commit=False,
                class_=AsyncSession,
            ),
            scopefunc=current_task,
        )

    async def dispatch(
        self, request: Request, next: RequestResponseEndpoint
    ) -> Response:
        session = self._session_factory()
        context = get_request_context()
        context[self.KEY] = session

        try:
            response = await next(request)
            code = response.status_code

            if code and code < status.HTTP_400_BAD_REQUEST:
                # await session.commit()
                logger.info("Everything is fine")
            else:
                logger.info(f"Bad response status({code}), rollback")
                # await session.rollback()
        except Exception as exc:
            # await session.rollback()
            raise exc
        finally:
            del context[self.KEY]
            await session.close()

        return response


def get_session() -> AsyncSession:
    context = get_request_context()
    # we want to raise error if KEY not in context
    return context[DatabaseSessionMiddleware.KEY]


async def check_database_connection(
    session: AsyncSession = Depends(get_session),
) -> bool:
    try:
        await session.execute("SELECT 1")
        return True
    except Exception as exc:  # noqa
        logger.error(str(exc))
        logger.error("READINESS: database connection")
        return False


def initialize_database_middleware(
    application: FastAPI, config: ClickhouseConfiguration, health_checks: list
) -> None:
    application.add_middleware(DatabaseSessionMiddleware, config=config)
    health_checks.append(check_database_connection)
