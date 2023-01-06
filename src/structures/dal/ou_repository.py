import logging

from fastapi import Depends
from neo4j import AsyncSession, AsyncTransaction

from src.common.models import Pagination, PaginationQueryParams
from src.common.neo4j import get_session, get_transaction
from src.structures.dal.utils import transform_to_dict
from src.structures.domain.organization_units.models import (
    OrganizationUnit,
    OrganizationUnitCreateDto,
    OrganizationUnitFindDto,
    OrganizationUnitPaginated,
)

logger = logging.getLogger(__name__)


class OrganizationUnitsRepository:
    def __init__(
        self,
        session: AsyncSession = Depends(get_session),
        transaction: AsyncTransaction | None = Depends(get_transaction),
    ) -> None:
        self.session = session
        self.transaction = transaction
        self.tx = transaction if transaction else session

    def _check_transaction(self):
        if self.transaction is None:
            raise Exception("This operation should be done in transactions")

    async def create(
        self,
        dto: OrganizationUnitCreateDto,
        parent_id: str,
    ) -> OrganizationUnit:
        # TODO: create model with mandatory parent
        self._check_transaction()

        params = transform_to_dict(dto)

        query = "MATCH (p:ORGANIZATION_UNIT|ROOT_ORGANIZATION_UNIT {id: $parent_id}) \n"
        query += "CREATE (ou:ORGANIZATION_UNIT { "

        params["active"] = False

        lines = []
        lines.append("id: randomUUID()")
        for key in params:
            lines.append(f"{key}: ${key}")

        query += ", ".join(lines)
        query += "})"
        query += "-[r:CHILD_OF]->(p)"
        query += "RETURN ou"

        params["parent_id"] = parent_id

        print(query)

        result = await (await self.tx.run(query, **params)).single()

        return OrganizationUnit(**result["ou"])

    async def delete(self, ou: OrganizationUnit) -> None:
        self._check_transaction()

        query = "MATCH (ou:ORGANIZATION_UNIT { id: $id }) SET ou.deleted = true"

        await (await self.tx.run(query, id=ou.id)).single()

    async def save(self, ou: OrganizationUnit) -> OrganizationUnit:
        self._check_transaction()

        params = transform_to_dict(ou)
        query = "MATCH (ou:ORGANIZATION_UNIT { id: $id }) SET "

        del params["id"]

        lines = []
        for key in params:
            lines.append(f"ou.{key} = ${key}")

        query += ", ".join(lines)
        query += " RETURN ou\n"

        print(query)

        result = await (await self.tx.run(query, **params, id=ou.id)).single()

        return OrganizationUnit(**result["ou"])

    async def get_by_id(self, id: str) -> OrganizationUnit:
        query = (
            "MATCH (ou:ORGANIZATION_UNIT {id: $id}) WHERE ou.deleted IS NULL RETURN ou"
        )
        result = await (await self.tx.run(query, id=id)).single()

        print(result)

        return OrganizationUnit(**result["ou"]) if result is not None else None

    async def find(
        self,
        dto: OrganizationUnitFindDto,
        available_ou: list[str],
        pagination: PaginationQueryParams,
    ) -> OrganizationUnitPaginated:
        params = transform_to_dict(dto)

        # TODO: make OU find DTO without child_of
        if "child_of" in params:
            del params["child_of"]

        # searching across available OU
        query = "MATCH (p:ORGANIZATION_UNIT|ROOT_ORGANIZATION_UNIT) WHERE p.id IN $available_ou "
        query += "MATCH (ou:ORGANIZATION_UNIT)-[:CHILD_OF*..10]->(p)"  # max 10 hops

        lines = []
        if params:
            # query += " WHERE "
            for key in params:
                lines.append(f"ou.{key} = ${key}")

        if lines:
            query += " WHERE " + " ".join(lines)

        count_query = str(query)
        count_query += " RETURN count(ou) as count"

        logger.debug(count_query)

        # TODO: we can run count and query concurrently to decrease latency
        count_result = await (
            await self.tx.run(count_query, available_ou=available_ou, **params),
        ).single()

        query += " RETURN ou"
        query += (
            f" SKIP {(pagination.page - 1) * pagination.limit} LIMIT {pagination.limit}"
        )

        # TODO: count

        logger.debug(query)

        result = await self.tx.run(query, available_ou=available_ou, **params)
        result_pagination = Pagination(
            page=pagination.page,
            limit=pagination.limit,
            count=count_result["count"],
        )

        # TODO: check that all readed at once
        retval = []
        async for record in result:
            retval.append(OrganizationUnit(**record["ou"]))

        return OrganizationUnitPaginated(pagination=result_pagination, data=retval)

    async def change_parent_ou(
        self,
        ou: OrganizationUnit,
        new_parent_id: str,
    ):
        pass
