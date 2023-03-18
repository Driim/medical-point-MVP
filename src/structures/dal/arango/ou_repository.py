import logging
from uuid import uuid4

from aioarango.database import StandardDatabase
from fastapi import Depends

from src.common.arango.middleware import get_session
from src.common.models import PaginationQueryParams
from src.structures.dal.neo4j.utils import transform_to_dict
from src.structures.domain.organization_units.models import OrganizationUnitCreateDto, OrganizationUnitBase, \
    OrganizationUnitFindDto, OrganizationUnitPaginated

logger = logging.getLogger(__name__)


class ArangoOrganizationUnitsRepository:
    COLLECTION = "organizations_units"
    GRAPH = "organization_graph"
    EDGE = "child_of"

    def __init__(self, database: StandardDatabase = Depends(get_session)):
        self.database = database

    async def create(
            self,
            dto: OrganizationUnitCreateDto,
            parent_id: str,
    ) -> OrganizationUnitBase:
        params = transform_to_dict(dto)
        params["parent_id"] = parent_id
        params["_key"] = str(uuid4())

        graph = self.database.graph(self.GRAPH)
        ou_collection = graph.vertex_collection(self.COLLECTION)
        ou_edges = graph.edge_collection(self.EDGE)

        parent = await ou_collection.get(parent_id)

        logger.info(parent)

        metadata = await ou_collection.insert(params)

        logger.info(parent)

        await ou_edges.link(metadata['_id'], parent['_id'])

        params["id"] = params["_key"]
        params["parent_organization_unit"] = parent_id

        return OrganizationUnitBase(**params)

    async def delete(self, ou: OrganizationUnitBase) -> None:
        pass

    async def save(self, ou: OrganizationUnitBase) -> OrganizationUnitBase:
        pass

    async def get_by_id(self, organization_unit_id: str) -> OrganizationUnitBase:
        graph = self.database.graph(self.GRAPH)
        ou_collection = graph.vertex_collection(self.COLLECTION)

        ou = await ou_collection.get(organization_unit_id)

        # getting parent
        cursor = await self.database.aql.execute(
            'FOR v IN 1..1 OUTBOUND @child child_of RETURN v._key',
            bind_vars={'child': ou.get('_id')}
        )
        parent_id = await cursor.next()

        return OrganizationUnitBase(
            id=ou['_key'],
            name=ou['name'],
            inn=ou['inn'],
            kpp=ou['kpp'],
            active=ou['active'],
            filler=ou.get('filler'),
            parent_organization_unit=parent_id
        )

    async def find(
            self,
            dto: OrganizationUnitFindDto,
            available_ou: list[str],
            pagination: PaginationQueryParams,
    ) -> OrganizationUnitPaginated:
        pass

    async def change_parent_ou(
            self,
            ou: OrganizationUnitBase,
            new_parent_id: str,
    ) -> OrganizationUnitBase:
        pass

    async def path_to_organization_unit(
            self,
            organization_unit: str,
            root_ou: str,
    ) -> list[str]:
        # TODO: implement
        cursor = await self.database.aql.execute(
            """
            FOR e IN OUTBOUND 
            SHORTEST_PATH @start 
            TO @end child_of 
            RETURN e._key
            """,
            bind_vars={
                'start': "organizations_units/" + organization_unit,
                'end': "organizations_units/" + root_ou,
            }
        )

        return [doc async for doc in cursor]

    async def is_in_active_tree(self, organization_unit: str, root_ou: str) -> bool:
        cursor = await self.database.aql.execute(
            """
            FOR e IN OUTBOUND 
            SHORTEST_PATH @start 
            TO @end child_of 
            RETURN e.active
            """,
            bind_vars={
                'start': "organizations_units/" + organization_unit,
                'end': "organizations_units/" + root_ou,
            }
        )

        state = [doc async for doc in cursor]

        logger.info(state)
        return False if False in state else True
