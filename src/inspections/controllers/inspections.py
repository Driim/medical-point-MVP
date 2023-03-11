# flake8: noqa: S311
import logging
import random
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, FastAPI
from fastapi_restful.cbv import cbv

from src.common.auth import get_user_id
from src.common.models import PaginationQueryParams
from src.imports.generators import get_bool_with_80_percent_chance_to_have_true
from src.inspections.domain.inspections.models import (
    Inspection,
    InspectionsFindBByWorkerDto,
    InspectionsFindDto,
    InspectionsPaginatedDto,
)
from src.inspections.domain.inspections.service import InspectionService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Inspections"])


@cbv(router)
class InspectionsController:
    inspections_service: InspectionService = Depends(InspectionService)

    @router.get("/worker_inspections", response_model=list[Inspection])
    async def find_inspections_by_worker(
        self,
        from_datetime: datetime | None = None,
        worker_id: str | None = None,
    ):
        dto = InspectionsFindBByWorkerDto(
            worker_id=worker_id,
            from_datetime=from_datetime,
        )
        return await self.inspections_service.find_inspections_by_worker(dto)

    @router.get("/workers/{worker_id}", response_model=list[Inspection])
    async def find_inspections_by_worker_for_test(
        self,
        worker_id: str,
    ):
        from_datetime = None
        if get_bool_with_80_percent_chance_to_have_true():
            from_datetime = datetime.today() - timedelta(days=1)

        dto = InspectionsFindBByWorkerDto(
            worker_id=worker_id,
            from_datetime=from_datetime,
        )
        return await self.inspections_service.find_inspections_by_worker(dto)

    @router.get("/devices/{device_id}", response_model=list[Inspection])
    async def test_find_inspections_by_device_id(
        self,
        device_id: str,
    ):
        dto = InspectionsFindDto(
            device_id=device_id,
        )

        pagination = PaginationQueryParams(
            page=1,
            limit=100,
        )

        return await self.inspections_service.find_inspections(
            dto, pagination, "b75de436-e162-43a7-8f1a-ebaa26c74b69"
        )

    @router.get("/testing-inspections", response_model=InspectionsPaginatedDto)
    async def find_inspections_testing(self):
        dto = self.form_dto()

        pagination = PaginationQueryParams(
            page=1,
            limit=100,
        )

        return await self.inspections_service.find_inspections(
            dto, pagination, "b75de436-e162-43a7-8f1a-ebaa26c74b69"
        )

    @router.get("/inspections", response_model=InspectionsPaginatedDto)
    async def find_inspections(
        self,
        worker_id: str | None = None,
        from_datetime: datetime | None = None,
        to_datetime: datetime | None = None,
        ou_id: str | None = None,
        device_id: str | None = None,
        user_id: str = Depends(get_user_id),
        pagination: PaginationQueryParams = Depends(PaginationQueryParams),
    ):
        dto = InspectionsFindDto(
            worker_id=worker_id,
            from_datetime=from_datetime,
            to_datetime=to_datetime,
            ou_id=ou_id,
            device_id=device_id,
        )
        return await self.inspections_service.find_inspections(dto, pagination, user_id)

    def form_dto(self) -> InspectionsFindDto:
        # TODO: generate random query DTO
        return InspectionsFindDto(
            from_datetime=datetime.today() - timedelta(days=random.randint(5, 10)),
            to_datetime=datetime.today() - timedelta(days=random.randint(0, 5)),
        )


def register_inspections_router(applications: FastAPI, version: str) -> None:
    logger.debug("Registering inspections controller")
    router.tags.append(version)
    applications.include_router(router, prefix=version)
