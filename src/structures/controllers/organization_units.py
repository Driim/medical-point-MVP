import logging
from typing import Optional

from fastapi import APIRouter, Depends, FastAPI
from fastapi_restful.cbv import cbv

from src.common.auth.auth import get_user_id
from src.common.models import PaginationQueryParams
from src.common.neo4j import Transactional, TransactionalRouter
from src.structures.domain.organization_units.models import (
    OrganizationUnit,
    OrganizationUnitCreateDto,
    OrganizationUnitFindDto,
    OrganizationUnitPaginated,
    OrganizationUnitUpdateDto,
)
from src.structures.domain.organization_units.service import OrganizationUnitService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Organization Units"], route_class=TransactionalRouter)


@cbv(router)
class OrganizationUnitsController:
    service: OrganizationUnitService = Depends(OrganizationUnitService)
    user_id: Optional[str] = Depends(get_user_id)

    @router.get("/organization-units/{id}", response_model=OrganizationUnit)
    async def get_organization_unit(self, id: str):
        return await self.service.get_by_id(id, self.user_id)

    @router.get("/organization-units", response_model=OrganizationUnitPaginated)
    async def find_organization_units(
        self,
        pagination: PaginationQueryParams = Depends(PaginationQueryParams),
        active: bool | None = None,
        child_of: str | None = None,
    ):
        dto = OrganizationUnitFindDto(active=active, child_of=child_of)
        return await self.service.find(dto, pagination, self.user_id)

    @Transactional()
    @router.post("/organization-units", response_model=OrganizationUnit)
    async def create_organization_unit(self, dto: OrganizationUnitCreateDto):
        return await self.service.create(dto, self.user_id)

    @Transactional()
    @router.put("/organization-units/{id}", response_model=OrganizationUnit)
    async def update_organization_unit(
        self,
        id: str,
        dto: OrganizationUnitUpdateDto,
    ):
        return await self.service.update(id, dto, self.user_id)

    @Transactional()
    @router.delete("/organization-units/{id}")
    async def delete_organization_unit(
        self,
        id: str,
    ):
        return await self.service.delete(id, self.user_id)

    @Transactional()
    @router.patch("/organization-units/{id}/activate", response_model=OrganizationUnit)
    async def activate_organization_unit(
        self,
        id: str,
    ):
        return await self.service.activate(id, self.user_id)

    @Transactional()
    @router.patch(
        "/organization-units/{id}/deactivate",
        response_model=OrganizationUnit,
    )
    async def deactivate_organization_unit(self, id: str):
        return await self.service.deactivate(id, self.user_id)

    @Transactional()
    @router.patch(
        "/organization-units/{id}/change-parent/{new_parent}",
        response_model=OrganizationUnit,
    )
    async def change_parent_organization_unit(self, id: str, new_parent: str):
        return await self.service.change_parent(id, new_parent, self.user_id)


def register_organization_units_router(application: FastAPI, version: str) -> None:
    logger.debug("Registering organization units controller")
    router.tags.append(version)
    application.include_router(router, prefix=version)
