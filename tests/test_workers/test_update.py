# flake8: noqa: C812
import pytest
from async_asgi_testclient import TestClient
from async_asgi_testclient.response import Response

from src.structures.domain.workers.models import WorkerUpdateDto


async def update_worker(
    client: TestClient, worker_id: str, user_id: str, dto: WorkerUpdateDto
) -> Response:
    return await client.put(
        f"/workers/{worker_id}", headers={"X-User-Id": user_id}, data=dto.json()
    )


class TestOutletUpdate:
    @pytest.mark.asyncio
    async def test_with_root_access_can_update_root_child(
        self, client: TestClient, child_ou_worker: str, user_id_with_root_access: str
    ):
        dto = WorkerUpdateDto(fio="New Name")
        result = await update_worker(
            client, child_ou_worker, user_id_with_root_access, dto
        )

        assert result.status_code == 200
        assert result.json()["fio"] == "New Name"

    @pytest.mark.asyncio
    async def test_without_root_access_can_not_update_root_child(
        self,
        client: TestClient,
        user_id_with_child_access: str,
        other_child_ou_worker: str,
    ):
        dto = WorkerUpdateDto(fio="New Name")
        result = await update_worker(
            client, other_child_ou_worker, user_id_with_child_access, dto
        )

        assert result.status_code == 403

    @pytest.mark.asyncio
    async def test_with_child_access_can_update_worker_for_child(
        self, client: TestClient, user_id_with_child_access: str, child_ou_worker: str
    ):
        dto = WorkerUpdateDto(fio="New Name")
        result = await update_worker(
            client, child_ou_worker, user_id_with_child_access, dto
        )

        assert result.status_code == 200
        assert result.json()["fio"] == "New Name"

    @pytest.mark.asyncio
    async def test_with_child_access_can_update_worker_for_child_of_child(
        self,
        client: TestClient,
        user_id_with_child_access: str,
        child_of_child_ou_worker: str,
    ):
        dto = WorkerUpdateDto(fio="New Name")
        result = await update_worker(
            client, child_of_child_ou_worker, user_id_with_child_access, dto
        )

        assert result.status_code == 200
        assert result.json()["fio"] == "New Name"
