import logging

from fastapi import APIRouter, Depends, FastAPI
from fastapi_restful.cbv import cbv

from src.inspections.domain.inspections.service import InspectionService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Generator"])


@cbv(router)
class GeneratorController:
    inspections_service: InspectionService = Depends(InspectionService)

    @router.get("/devices/{device_id}/exam/{worker_id}")
    async def generate_inspection(self, device_id: str, worker_id: str):
        return await self.inspections_service.generate_inspection(device_id, worker_id)


def register_generator_router(application: FastAPI, version: str) -> None:
    logger.debug("Registering generator controller")
    router.tags.append(version)
    application.include_router(router, prefix=version)
