import logging
from uuid import uuid4

from aioarango.database import StandardDatabase
from fastapi import Depends

from src.common.arango.middleware import get_session
from src.common.models import PaginationQueryParams
from src.structures.dal.neo4j.utils import transform_to_dict
from src.structures.domain.outlets.models import OutletBase, OutletCreateDto, OutletPaginated, OutletFindDto

logger = logging.getLogger(__name__)


class ArangoOutletsRepository:
    COLLECTION = "outlets"
    OU_COLLECTION = "organizations_units"
    GRAPH = "outlets_graph"
    EDGE = "belong_to"

    def __init__(self, database: StandardDatabase = Depends(get_session)):
        self.database = database

    async def create(self, dto: OutletCreateDto) -> OutletBase:
        params = transform_to_dict(dto)
        params["_key"] = str(uuid4())

        parent_id = dto.organization_unit_id

        graph = self.database.graph(self.GRAPH)
        collection = graph.vertex_collection(self.COLLECTION)
        ou_collection = graph.vertex_collection(self.OU_COLLECTION)
        edges = graph.edge_collection(self.EDGE)

        parent = await ou_collection.get(parent_id)
        outlet = await collection.insert(params)
        await edges.link(outlet['_id'], parent['_id'])

        params['id'] = outlet['_key']
        return OutletBase(
            **params
        )

    async def delete(self, outlet: OutletBase) -> None:
        pass

    async def save(self, outlet: OutletBase) -> OutletBase:
        pass

    async def get_by_id(self, outlet_id: str) -> OutletBase:
        graph = self.database.graph(self.GRAPH)
        collection = graph.vertex_collection(self.COLLECTION)

        worker = await collection.get(outlet_id)
        return OutletBase(
            id=worker['_key'],
            **worker
        )

    async def find(
            self,
            dto: OutletFindDto,
            available_ou: list[str],
            pagination: PaginationQueryParams,
    ) -> OutletPaginated:
        pass

    async def change_parent_ou(
            self,
            outlet: OutletBase,
            new_parent_id: str,
    ) -> OutletBase:
        pass


