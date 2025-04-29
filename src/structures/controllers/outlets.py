import logging
from typing import Optional

from fastapi import APIRouter, Depends, FastAPI, status
from fastapi_restful.cbv import cbv

from src.common.auth import get_user_id
from src.common.models import PaginationQueryParams
from src.structures.domain.outlets.models import (
    Outlet,
    OutletCreateDto,
    OutletFindDto,
    OutletPaginated,
    OutletUpdateDto,
)
from src.structures.domain.outlets.service import OutletService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Outlets"])


@cbv(router)
class OutletsController:
    user_id: Optional[str] = Depends(get_user_id)
    service: OutletService = Depends(OutletService)

    @router.get("/outlets/{outlet_id}", response_model=Outlet)
    async def get_outlet(self, outlet_id: str):
        return await self.service.get_by_id(outlet_id, self.user_id)

    @router.get("/outlets", response_model=OutletPaginated)
    async def find_outlets(
        self,
        pagination: PaginationQueryParams = Depends(PaginationQueryParams),
        active: bool | None = None,
        child_of: str | None = None,
    ):
        dto = OutletFindDto(
            child_of=child_of,
            active=active,
        )

        return await self.service.find(dto, pagination, self.user_id)

    @router.post(
        "/outlets",
        response_model=Outlet,
        status_code=status.HTTP_201_CREATED,
    )
    async def create_outlet(self, dto: OutletCreateDto):
        return await self.service.create(dto, self.user_id)

    @router.put("/outlets/{outlet_id}", response_model=Outlet)
    async def update_outlet(self, outlet_id: str, dto: OutletUpdateDto):
        return await self.service.update(outlet_id, dto, self.user_id)

    @router.delete("/outlets/{outlet_id}")
    async def delete_outlet(self, outlet_id: str):
        return await self.service.delete(outlet_id, self.user_id)

    @router.patch("/outlets/{outlet_id}/activate", response_model=Outlet)
    async def activate_outlet(
        self,
        outlet_id: str,
    ):
        return await self.service.activate(outlet_id, self.user_id)

    @router.patch("/outlets/{outlet_id}/deactivate", response_model=Outlet)
    async def deactivate_outlet(self, outlet_id: str):
        return await self.service.deactivate(outlet_id, self.user_id)

    @router.patch(
        "/outlets/{outlet_id}/change-parent/{new_parent_id}",
        response_model=Outlet,
    )
    async def change_parent_organization_unit(self, outlet_id: str, new_parent_id: str):
        return await self.service.change_organization(
            outlet_id,
            new_parent_id,
            self.user_id,
        )


def register_outlets_router(application: FastAPI, version: str) -> None:
    logger.debug("Registering outlets controller")
    router.tags.append(version)
    application.include_router(router, prefix=version)
