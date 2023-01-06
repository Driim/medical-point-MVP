import logging
from typing import Callable

from fastapi import Request, Response, status
from fastapi.routing import APIRoute
from neo4j import AsyncTransaction

from src.common.context import get_request_context

from .middleware import get_session

logger = logging.getLogger(__name__)


class TransactionalRouter(APIRoute):
    KEY = "neo4j_transaction"

    async def _commit_or_rollback_transaction(
        self,
        transactional: bool,
        code: int,
        transaction: AsyncTransaction,
    ):
        if transactional and code < status.HTTP_400_BAD_REQUEST:
            await transaction.commit()
        elif transactional:
            logger.info(f"Bad response status({code}), rollback")
            await transaction.rollback()

    def _is_transactional(self, request: Request) -> bool:
        if "endpoint" in request.scope and hasattr(
            request.scope["endpoint"],
            "__transactional__",
        ):
            return True

        return False

    def get_route_handler(self) -> Callable:
        # We can get handler function only in APIRoute
        # So, if function has __transactional__ we should open transaction
        # Session could only have one transaction, so we do not need to save it anyware
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            transactional = self._is_transactional(request)

            transaction: AsyncTransaction = None
            if transactional:
                logger.debug("Transactional method, starting transaction...")
                session = get_session()
                transaction = await session.begin_transaction()

                context = get_request_context()
                context[self.KEY] = transaction

            try:
                response = await original_route_handler(request)
                code = response.status_code

                await self._commit_or_rollback_transaction(
                    transactional,
                    code,
                    transaction,
                )
            except Exception as exc:
                if transactional:
                    await transaction.rollback()
                raise exc
            finally:
                if transactional:
                    del context[self.KEY]

            return response

        return custom_route_handler


def get_transaction() -> AsyncTransaction | None:
    context = get_request_context()
    return context.get(TransactionalRouter.KEY, None)
