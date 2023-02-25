import httpx
from fastapi import Depends, HTTPException, Request

from src.common.context.context import get_request
from src.structures.domain.devices.models import DeviceExamForWorker


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
