import logging
from uuid import uuid4

from aioarango.database import StandardDatabase
from fastapi import Depends

from src.common.arango.middleware import get_session
from src.common.models import PaginationQueryParams
from src.structures.dal.neo4j.utils import transform_to_dict
from src.structures.domain.workers.models import WorkerCreateDto, WorkerBase, WorkerPaginatedDto, WorkerFindDto

logger = logging.getLogger(__name__)


class ArangoWorkersRepository:
    COLLECTION = "workers"
    OU_COLLECTION = "organizations_units"
    GRAPH = "workers_graph"
    EDGE = "work_in"

    def __init__(self, database: StandardDatabase = Depends(get_session)):
        self.database = database

    async def create(self, dto: WorkerCreateDto) -> WorkerBase:
        params = transform_to_dict(dto)
        params["_key"] = str(uuid4())

        parent_id = params['organization_unit_id']

        graph = self.database.graph(self.GRAPH)
        collection = graph.vertex_collection(self.COLLECTION)
        ou_collection = graph.vertex_collection(self.OU_COLLECTION)
        edges = graph.edge_collection(self.EDGE)

        parent = await ou_collection.get(parent_id)
        worker = await collection.insert(params)
        await edges.link(worker['_id'], parent['_id'])

        params['id'] = worker['_key']
        return WorkerBase(
            **params
        )

    async def delete(self, worker: WorkerBase) -> None:
        pass

    async def save(self, worker: WorkerBase) -> WorkerBase:
        pass

    async def get_by_id(self, worker_id: str) -> WorkerBase:
        graph = self.database.graph(self.GRAPH)
        collection = graph.vertex_collection(self.COLLECTION)

        worker = await collection.get(worker_id)
        return WorkerBase(
            id=worker['_key'],
            **worker
        )

    async def find(
            self,
            dto: WorkerFindDto,
            available_ou: list[str],
            pagination: PaginationQueryParams,
    ) -> WorkerPaginatedDto:
        pass

    async def change_parent_ou(
            self,
            worker: WorkerBase,
            new_parent_id: str,
    ) -> WorkerBase:
        pass



