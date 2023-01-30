import logging

from fastapi import Depends
from neo4j import AsyncSession, AsyncTransaction

from src.common.models import Pagination, PaginationQueryParams
from src.common.neo4j import get_session, get_transaction
from src.common.utils.cypher_utils import (
    prepare_create_query,
    prepare_delete_query,
    prepare_find_query,
    prepare_get_by_id_query,
    prepare_save_query,
)
from src.structures.dal.utils import transform_to_dict
from src.structures.domain.workers.models import (
    WorkerBase,
    WorkerCreateDto,
    WorkerFindDto,
    WorkerPaginatedDto,
)

logger = logging.getLogger(__name__)


class WorkersRepository:
    node_labels: list[str] = ["Worker"]
    relation: str = "WORK_IN"

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

    async def create(self, dto: WorkerCreateDto) -> WorkerBase:
        self._check_transaction()

        params = transform_to_dict(dto)

        query = prepare_create_query(
            ["OrganizationUnit"],
            "organization_unit_id",
            self.node_labels,
            params,
            self.relation,
        )
        query += " RETURN o { .*, organization_unit_id: p.id } as worker"

        result = await (await self.tx.run(query, **params)).single()
        return WorkerBase(**result["worker"])

    async def delete(self, worker: WorkerBase) -> None:
        self._check_transaction()

        query = prepare_delete_query(self.node_labels)

        await (await self.tx.run(query, id=worker.id)).single()

    async def save(self, worker: WorkerBase) -> WorkerBase:
        self._check_transaction()

        params = transform_to_dict(worker)
        del params["id"]

        query = prepare_save_query(self.node_labels, self.relation, params)
        query += " RETURN o { .*, organization_unit_id: p.id } as worker\n"

        result = await (await self.tx.run(query, **params, id=worker.id)).single()
        return WorkerBase(**result["worker"])

    async def get_by_id(self, worker_id: str) -> WorkerBase:
        query = prepare_get_by_id_query(self.node_labels, self.relation)
        query += " RETURN o { .*, organization_unit_id: p.id } as worker\n"

        result = await (await self.tx.run(query, id=worker_id)).single()
        return WorkerBase(**result["worker"]) if result is not None else None

    async def find(
        self,
        dto: WorkerFindDto,
        available_ou: list[str],
        pagination: PaginationQueryParams,
    ) -> WorkerPaginatedDto:
        params = transform_to_dict(dto)
        lines = []
        if params:
            for key in params:
                lines.append(f"o.{key} = ${key}")

        query = prepare_find_query(
            ["OrganizationUnit", "RootOrganizationUnit"],
            self.node_labels,
            self.relation,
            lines,
        )

        count_query = str(query)
        count_query += " RETURN count(o) as count"

        count_result = await (
            await self.tx.run(count_query, available_ou=available_ou, **params)  # noqa
        ).single()

        query += " RETURN o"
        query += (
            f" SKIP {(pagination.page - 1) * pagination.limit} LIMIT {pagination.limit}"
        )

        result = await self.tx.run(query, available_ou=available_ou, **params)
        result_pagination = Pagination(
            page=pagination.page,
            limit=pagination.limit,
            count=count_result["count"],
        )

        retval = []
        async for record in result:
            retval.append(WorkerBase(**record["o"]))

        return WorkerPaginatedDto(pagination=result_pagination, data=retval)

    async def change_parent_ou(
        self,
        worker: WorkerBase,
        new_parent_id: str,
    ) -> WorkerBase:
        query = "MATCH (n_parent:OrganizationUnit { id: $new_parent_id }) "
        query += prepare_get_by_id_query(self.node_labels, self.relation)
        query += " DELETE r "
        query += f"CREATE (o)-[:{self.relation}]->(n_parent)"

        await (
            await self.tx.run(query, id=worker.id, new_parent_id=new_parent_id)
        ).single()

        # worker also had organization_unit_id because uses uniq index,
        # so we need to update both relation and data
        worker.organization_unit_id = new_parent_id
        return await self.save(worker)
