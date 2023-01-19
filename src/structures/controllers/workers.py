import logging
from typing import Optional

from fastapi import APIRouter, Depends, FastAPI, status
from fastapi_restful.cbv import cbv

from src.common.auth import get_user_id
from src.common.models import PaginationQueryParams
from src.common.neo4j import Transactional, TransactionalRouter
from src.structures.domain.workers.models import (
    Worker,
    WorkerCreateDto,
    WorkerFindDto,
    WorkerPaginatedDto,
    WorkerUpdateDto,
)
from src.structures.domain.workers.service import WorkerService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Workers"], route_class=TransactionalRouter)


@cbv(router)
class WorkersController:
    user_id: Optional[str] = Depends(get_user_id)
    service: WorkerService = Depends(WorkerService)

    @router.get("/workers/{worker_id}", response_model=Worker)
    async def get_worker(self, worker_id: str):
        return await self.service.get_by_id(worker_id, self.user_id)

    @router.get("/workers", response_model=WorkerPaginatedDto)
    async def find_workers(
        self,
        pagination: PaginationQueryParams = Depends(PaginationQueryParams),
        active: bool | None = None,
        child_of_organization_unit: str | None = None,
    ):
        dto = WorkerFindDto(
            active=active,
            child_of_organization_unit=child_of_organization_unit,
        )
        return await self.service.find(dto, pagination, self.user_id)

    @Transactional()
    @router.post(
        "/workers",
        response_model=Worker,
        status_code=status.HTTP_201_CREATED,
    )
    async def create_worker(self, dto: WorkerCreateDto):
        return await self.service.create(dto, self.user_id)

    @Transactional()
    @router.put("/workers/{worker_id}", response_model=Worker)
    async def update_worker(self, worker_id: str, dto: WorkerUpdateDto):
        return await self.service.update(worker_id, dto, self.user_id)

    @Transactional()
    @router.delete("/workers/{worker_id}")
    async def delete_worker(self, worker_id: str):
        return await self.service.delete(worker_id, self.user_id)

    @Transactional()
    @router.patch("/workers/{worker_id}/activate", response_model=Worker)
    async def activate_worker(
        self,
        worker_id: str,
    ):
        return await self.service.activate(worker_id, self.user_id)

    @Transactional()
    @router.patch("/workers/{worker_id}/deactivate", response_model=Worker)
    async def deactivate_worker(self, worker_id: str):
        return await self.service.deactivate(worker_id, self.user_id)

    @Transactional()
    @router.patch(
        "/workers/{worker_id}/change-organization/{new_parent_id}",
        response_model=Worker,
    )
    async def change_organization_unit(self, worker_id: str, new_parent_id: str):
        return await self.service.change_parent(worker_id, new_parent_id, self.user_id)


def register_workers_router(application: FastAPI, version: str) -> None:
    logger.debug("Registering workers controller")
    router.tags.append(version)
    application.include_router(router, prefix=version)
