import logging

from fastapi import Depends
from neo4j import AsyncSession, AsyncTransaction

from src.common.models import Pagination, PaginationQueryParams
from src.common.neo4j import get_session, get_transaction
from src.structures.dal.utils import transform_to_dict
from src.structures.domain.organization_units.models import (
    OrganizationUnitBase,
    OrganizationUnitCreateDto,
    OrganizationUnitFindDto,
    OrganizationUnitPaginated,
    OrganizationUnitShort,
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
    ) -> OrganizationUnitBase:
        # TODO: create model with mandatory parent
        self._check_transaction()

        params = transform_to_dict(dto)

        query = "MATCH (p:OrganizationUnit|RootOrganizationUnit {id: $parent_id}) \n"
        query += "CREATE (ou:OrganizationUnit { "

        lines = ["id: randomUUID()"]
        for key in params:
            lines.append(f"{key}: ${key}")

        query += ", ".join(lines)
        query += "})-[r:CHILD_OF]->(p)"
        query += (
            " RETURN ou { .*, parent_organization_unit: p.id } as organization_unit"
        )

        params["parent_id"] = parent_id

        result = await (await self.tx.run(query, **params)).single()

        return OrganizationUnitBase(**result["organization_unit"])

    async def delete(self, ou: OrganizationUnitBase) -> None:
        self._check_transaction()

        query = "MATCH (ou:OrganizationUnit { id: $id }) SET ou.deleted = true"

        await (await self.tx.run(query, id=ou.id)).single()

    async def save(self, ou: OrganizationUnitBase) -> OrganizationUnitBase:
        self._check_transaction()

        params = transform_to_dict(ou)
        query = "MATCH (ou:OrganizationUnit { id: $id })-[r:CHILD_OF]->(p) SET "

        del params["id"]

        lines = []
        for key in params:
            lines.append(f"ou.{key} = ${key}")

        query += ", ".join(lines)
        query += (
            " RETURN ou { .*, parent_organization_unit: p.id } as organization_unit\n"
        )

        result = await (await self.tx.run(query, **params, id=ou.id)).single()

        return OrganizationUnitBase(**result["organization_unit"])

    async def get_by_id(self, organization_unit_id: str) -> OrganizationUnitBase:
        query = (
            "MATCH (ou:OrganizationUnit {id: $id})-[r:CHILD_OF]->(p)"
            + " WHERE ou.deleted IS NULL RETURN ou { .*, parent_organization_unit: p.id } as organization_unit"
        )

        result = await (await self.tx.run(query, id=organization_unit_id)).single()
        return (
            OrganizationUnitBase(**result["organization_unit"])
            if result is not None
            else None
        )

    async def find(
        self,
        dto: OrganizationUnitFindDto,
        available_ou: list[str],
        pagination: PaginationQueryParams,
    ) -> OrganizationUnitPaginated:
        params = transform_to_dict(dto)

        logger.warning(available_ou)

        # TODO: make OU find DTO without child_of
        if "child_of" in params:
            del params["child_of"]

        # searching across available OU
        query = "MATCH (p:OrganizationUnit|RootOrganizationUnit) WHERE p.id IN $available_ou "
        query += "MATCH (ou:OrganizationUnit)-[:CHILD_OF*0..10]->(p)"  # 1 to 10 hops

        lines = []
        if params:
            # query += " WHERE "
            for key in params:
                lines.append(f"ou.{key} = ${key}")

        if lines:
            query += " WHERE ou.deleted is NULL " + " ".join(lines)
        else:
            query += " WHERE ou.deleted is NULL "

        count_query = str(query)
        count_query += " RETURN count(ou) as count"

        logger.debug(count_query)

        # TODO: we can run count and query concurrently to decrease latency
        count_result = await (
            await self.tx.run(count_query, available_ou=available_ou, **params)  # noqa
        ).single()

        query += " RETURN ou"
        query += (
            f" SKIP {(pagination.page - 1) * pagination.limit} LIMIT {pagination.limit}"
        )

        logger.debug(query)

        result = await self.tx.run(query, available_ou=available_ou, **params)
        result_pagination = Pagination(
            page=pagination.page,
            limit=pagination.limit,
            count=count_result["count"],
        )

        # TODO: check that all read at once
        retval = []
        async for record in result:
            retval.append(OrganizationUnitShort(**record["ou"]))

        return OrganizationUnitPaginated(pagination=result_pagination, data=retval)

    async def change_parent_ou(
        self,
        ou: OrganizationUnitBase,
        new_parent_id: str,
    ) -> OrganizationUnitBase:
        query = "MATCH (ou:OrganizationUnit { id: $id })-[r:CHILD_OF]->(p) "
        query += "MATCH (n_parent:OrganizationUnit { id: $new_parent_id }) "
        query += "WHERE ou.deleted IS NULL AND n_parent.deleted IS NULL "
        query += "DELETE r "
        query += "CREATE (ou)-[:CHILD_OF]->(n_parent) "
        query += "RETURN ou { .*, parent_organization_unit: n_parent.id } as organization_unit"

        result = await (
            await self.tx.run(query, id=ou.id, new_parent_id=new_parent_id)
        ).single()

        return OrganizationUnitBase(**result["organization_unit"])

    async def path_to_organization_unit(
        self,
        organization_unit: str,
        root_ou: str,
    ) -> list[str]:
        query = "MATCH (o:OrganizationUnit {id: $organization_unit})"
        query += "-[:CHILD_OF*0..10]->(p:OrganizationUnit)-[:CHILD_OF*0..10]->(root:RootOrganizationUnit)"
        query += " RETURN collect(p.id) + [$root_ou] as path_ids"

        result = await (
            await self.tx.run(
                query,
                organization_unit=organization_unit,
                root_ou=root_ou,
            )  # noqa
        ).single()
        return result["path_ids"]
