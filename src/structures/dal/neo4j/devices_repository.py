import logging

from fastapi import Depends
from neo4j import AsyncSession, AsyncTransaction

from src.common.models import Pagination, PaginationQueryParams
from src.common.neo4j import get_session, get_transaction
from src.common.utils.cypher_utils import (
    prepare_create_query,
    prepare_delete_query,
    prepare_get_by_id_query,
    prepare_save_query,
)
from src.structures.dal.neo4j.utils import transform_to_dict
from src.structures.domain.devices.models import (
    DeviceBase,
    DeviceCreateDto,
    DeviceFindDto,
    DevicePaginatedDto,
)

logger = logging.getLogger(__name__)


class DevicesRepository:
    node_labels: list[str] = ["Device"]
    relation: str = "LOCATED_AT"

    def __init__(
        self,
        session: AsyncSession = Depends(get_session),
        transaction: AsyncTransaction | None = Depends(get_transaction),
    ):
        # TODO: move all this code to separate class
        self.session = session
        self.transaction = transaction
        self.tx = transaction if transaction else session

    def _check_transaction(self):
        if self.transaction is None:
            raise Exception("This operation should be done in transactions")

    async def create(self, dto: DeviceCreateDto) -> DeviceBase:
        self._check_transaction()

        params = transform_to_dict(dto)

        query = prepare_create_query(
            ["Outlet"],
            "outlet_id",
            self.node_labels,
            params,
            self.relation,
        )
        query += " RETURN o { .*, outlet_id: p.id } as device"

        result = await (await self.tx.run(query, **params)).single()
        return DeviceBase(**result["device"])

    async def delete(self, device: DeviceBase) -> None:
        self._check_transaction()

        query = prepare_delete_query(self.node_labels)

        await (await self.tx.run(query, id=device.id)).single()

    async def save(self, device: DeviceBase) -> DeviceBase:
        self._check_transaction()

        params = transform_to_dict(device)
        del params["id"]

        query = prepare_save_query(self.node_labels, self.relation, params)
        query += " RETURN o { .*, outlet_id: p.id } as device\n"

        result = await (await self.tx.run(query, **params, id=device.id)).single()
        return DeviceBase(**result["device"])

    async def get_by_id(self, device_id: str) -> DeviceBase:
        query = prepare_get_by_id_query(self.node_labels, self.relation)
        query += " RETURN o { .*, outlet_id: p.id } as device\n"

        result = await (await self.tx.run(query, id=device_id)).single()
        return DeviceBase(**result["device"]) if result is not None else None

    async def find(
        self,
        dto: DeviceFindDto,
        available_ou: list[str],
        available_outlets: list[str],
        pagination: PaginationQueryParams,
    ) -> DevicePaginatedDto:
        params = transform_to_dict(dto)

        if "child_of_outlet" in params:
            del params["child_of_outlet"]

        if "child_of_organization_unit" in params:
            del params["child_of_organization_unit"]

        lines = []
        if params:
            for key in params:
                lines.append(f"o.{key} = ${key}")

        query = ""

        if available_ou:
            query = f"MATCH (p:{'|'.join(['OrganizationUnit', 'RootOrganizationUnit'])}) WHERE p.id IN $available_ou "
            query += (
                f"MATCH (o:{'|'.join(self.node_labels)})-[:{self.relation}]"
                f"->(:Outlet)-[:BELONG_TO]->()-[:CHILD_OF*0..10]->(p)"
            )
            params["available_ou"] = available_ou

        if available_outlets:
            query = (
                f"MATCH (p:{'|'.join(['Outlet'])}) WHERE p.id IN $available_outlets "
            )
            query += (
                f"MATCH (o:{'|'.join(self.node_labels)})-[:{self.relation}]"
                f"->(p:Outlet)"
            )
            params["available_outlets"] = available_outlets

        query += " WHERE p.deleted IS NULL AND o.deleted IS NULL "
        if lines:
            query += " AND ".join(lines)

        count_query = str(query)
        count_query += " RETURN count(o) as count"

        count_result = await (await self.tx.run(count_query, **params)).single()  # noqa

        query += " RETURN o"
        query += (
            f" SKIP {(pagination.page - 1) * pagination.limit} LIMIT {pagination.limit}"
        )

        result = await self.tx.run(query, **params)
        result_pagination = Pagination(
            page=pagination.page,
            limit=pagination.limit,
            count=count_result["count"],
        )

        retval = []
        async for record in result:
            retval.append(DeviceBase(**record["o"]))

        return DevicePaginatedDto(pagination=result_pagination, data=retval)

    async def change_parent_outlet(
        self,
        device: DeviceBase,
        new_parent_id: str,
    ) -> DeviceBase:
        query = "MATCH (n_parent:Outlet { id: $new_parent_id }) "
        query += prepare_get_by_id_query(self.node_labels, self.relation)
        query += " DELETE r "
        query += f"CREATE (o)-[:{self.relation}]->(n_parent)"

        await (
            await self.tx.run(query, id=device.id, new_parent_id=new_parent_id)
        ).single()

        return await self.get_by_id(device.id)

    async def can_take_exam_on_device(self, device_id: str, worker_id: str) -> bool:
        # TODO: Refactor
        query = f"MATCH (d:{'|'.join(self.node_labels)} {{id: $device_id}})-[:{self.relation}]->(o:Outlet)"
        query += "-[:BELONG_TO]->(ou:OrganizationUnit)<-[:WORK_IN]-(w:Worker {id: $worker_id}) "
        query += "WHERE d.deleted IS NULL and o.deleted IS NULL and ou.deleted IS NULL and w.deleted IS NULL "
        query += "and toBoolean(d.active) = true and toBoolean(o.active) = true "
        query += "and toBoolean(ou.active) = true and toBoolean(w.active) = true "
        query += "RETURN ou"

        result = await (
            await self.tx.run(query, device_id=device_id, worker_id=worker_id)
        ).single()

        if result:
            return True

        return False

    async def org_have_agreement(self, device_id: str, worker_id: str) -> bool:
        # TODO: implement
        return False
