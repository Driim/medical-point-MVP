import logging
from typing import Optional

from fastapi import APIRouter, Depends, FastAPI, status
from fastapi_restful.cbv import cbv

from src.common.auth import get_user_id
from src.common.models import PaginationQueryParams
from src.common.neo4j import Transactional, TransactionalRouter
from src.structures.domain.devices.models import (
    Device,
    DeviceCreateDto,
    DeviceFindDto,
    DevicePaginatedDto,
    DeviceUpdateDto,
)
from src.structures.domain.devices.service import DeviceService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Devices"], route_class=TransactionalRouter)


@cbv(router)
class DevicesController:
    user_id: Optional[str] = Depends(get_user_id)
    service: DeviceService = Depends(DeviceService)

    @router.get("/devices/{device_id}", response_model=Device)
    async def get_device(self, device_id: str):
        return await self.service.get_by_id(device_id, self.user_id)

    @router.get("/devices", response_model=DevicePaginatedDto)
    async def find_devices(
        self,
        pagination: PaginationQueryParams = Depends(PaginationQueryParams),
        active: bool | None = None,
        child_of_organization_unit: str | None = None,
        child_of_outlet: str | None = None,
    ):
        dto = DeviceFindDto(
            child_of_organization_unit=child_of_organization_unit,
            child_of_outlet=child_of_outlet,
            active=active,
        )
        return await self.service.find(dto, pagination, self.user_id)

    @Transactional()
    @router.post(
        "/devices",
        response_model=Device,
        status_code=status.HTTP_201_CREATED,
    )
    async def create_device(self, dto: DeviceCreateDto):
        return await self.service.create(dto, self.user_id)

    @Transactional()
    @router.put("/devices/{device_id}", response_model=Device)
    async def update_device(self, device_id: str, dto: DeviceUpdateDto):
        return await self.service.update(device_id, dto, self.user_id)

    @Transactional()
    @router.delete("/devices/{device_id}")
    async def delete_device(self, device_id: str):
        return await self.service.delete(device_id, self.user_id)

    @Transactional()
    @router.patch("/devices/{device_id}/activate", response_model=Device)
    async def activate_device(
        self,
        device_id: str,
    ):
        return await self.service.activate(device_id, self.user_id)

    @Transactional()
    @router.patch("/devices/{device_id}/deactivate", response_model=Device)
    async def deactivate_outlet(self, device_id: str):
        return await self.service.deactivate(device_id, self.user_id)

    @Transactional()
    @router.patch(
        "/devices/{device_id}/change-outlet/{new_outlet_id}",
        response_model=Device,
    )
    async def change_outlet(self, device_id: str, new_outlet_id: str):
        return await self.service.change_outlet(device_id, new_outlet_id, self.user_id)


def register_devices_router(application: FastAPI, version: str) -> None:
    logger.debug("Registering devices controller")
    router.tags.append(version)
    application.include_router(router, prefix=version)
