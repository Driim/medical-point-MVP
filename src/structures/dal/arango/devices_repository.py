import logging
from uuid import uuid4

from aioarango.database import StandardDatabase
from fastapi import Depends

from src.common.arango.middleware import get_session
from src.common.models import PaginationQueryParams
from src.structures.dal.neo4j.utils import transform_to_dict
from src.structures.domain.devices.models import DeviceCreateDto, DeviceBase, DevicePaginatedDto, DeviceFindDto

logger = logging.getLogger(__name__)


class ArangoDevicesRepository:
    COLLECTION = "devices"
    OUTLETS_COLLECTION = "outlets"
    GRAPH = "devices_graph"
    EDGE = "located_at"

    def __init__(self, database: StandardDatabase = Depends(get_session)):
        self.database = database

    async def create(self, dto: DeviceCreateDto) -> DeviceBase:
        params = transform_to_dict(dto)
        params["_key"] = str(uuid4())

        parent_id = dto.outlet_id

        graph = self.database.graph(self.GRAPH)
        collection = graph.vertex_collection(self.COLLECTION)
        outlet_collection = graph.vertex_collection(self.OUTLETS_COLLECTION)
        edges = graph.edge_collection(self.EDGE)

        parent = await outlet_collection.get(parent_id)
        device = await collection.insert(params)
        await edges.link(device['_id'], parent['_id'])

        params['id'] = device['_key']
        return DeviceBase(
            **params
        )

    async def delete(self, device: DeviceBase) -> None:
        pass

    async def save(self, device: DeviceBase) -> DeviceBase:
        pass

    async def get_by_id(self, device_id: str) -> DeviceBase:
        graph = self.database.graph(self.GRAPH)
        collection = graph.vertex_collection(self.COLLECTION)

        device = await collection.get(device_id)
        return DeviceBase(
            id=device['_key'],
            **device
        )

    async def find(
            self,
            dto: DeviceFindDto,
            available_ou: list[str],
            available_outlets: list[str],
            pagination: PaginationQueryParams,
    ) -> DevicePaginatedDto:
        pass

    async def change_parent_outlet(
            self,
            device: DeviceBase,
            new_parent_id: str,
    ) -> DeviceBase:
        pass

    async def can_take_exam_on_device(self, device_id: str, worker_id: str) -> bool:
        # Not needed, check is in service
        return True

    async def org_have_agreement(self, device_id: str, worker_id: str) -> bool:
        # TODO: implement
        return False
