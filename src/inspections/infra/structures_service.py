import logging

import httpx
from fastapi import Depends, HTTPException, Request

from src.common.context.context import get_request
from src.structures.domain.devices.models import DeviceExamForWorker

logger = logging.getLogger(__name__)


class StructuresService:
    def __init__(
        self,
        request: Request = Depends(get_request),
    ):
        self._request = request

    async def worker_can_take_exam(
        self, device_id: str, worker_id: str
    ) -> DeviceExamForWorker:
        async with httpx.AsyncClient() as client:
            result = await client.get(
                f"http://{self._request.app.state.STRUCTURES_URL}/devices/{device_id}/exam/{worker_id}",
            )
            # json -> DeviceExamForWorker
            if result.status_code == 200:
                return DeviceExamForWorker(**result.json())
            else:
                raise HTTPException(status_code=403)

    async def get_available_ou_for_user(self, user_id: str) -> list[str]:
        async with httpx.AsyncClient() as client:
            result = await client.get(
                f"http://{self._request.app.state.STRUCTURES_URL}/users/{user_id}",
            )

            if result.status_code == 200:
                logger.debug(result.json())
                return result.json()["read"]
            else:
                raise HTTPException(status_code=404)
