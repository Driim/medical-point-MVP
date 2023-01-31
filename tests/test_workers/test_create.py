import pytest
from async_asgi_testclient import TestClient

from src.structures.domain.workers.models import WorkerCreateDto
from tests.helpers import create_worker


class TestWorkerCreate:
    @pytest.mark.asyncio
    async def test_with_root_access_can_create_worker_for_root_child(
        self, client: TestClient, user_id_with_root_access: str, child_ou: str
    ):
        result = await create_worker(client, child_ou, user_id_with_root_access)

        assert result.status_code == 201

    @pytest.mark.asyncio
    async def test_without_root_access_can_not_create_worker_for_root_child(
        self, client: TestClient, other_child_ou: str, user_id_with_child_access: str
    ):
        result = await create_worker(client, other_child_ou, user_id_with_child_access)

        assert result.status_code == 403

    @pytest.mark.asyncio
    async def test_with_child_access_can_create_worker_for_child(
        self, client: TestClient, child_ou: str, user_id_with_child_access: str
    ):
        result = await create_worker(client, child_ou, user_id_with_child_access)

        assert result.status_code == 201

    @pytest.mark.asyncio
    async def test_with_child_access_can_create_worker_for_child_of_child(
        self, client: TestClient, user_id_with_child_access: str, child_of_child_ou: str
    ):
        result = await create_worker(
            client, child_of_child_ou, user_id_with_child_access
        )

        assert result.status_code == 201

    @pytest.mark.asyncio
    async def test_you_can_create_two_workers_with_same_driver_license_in_ou(
        self, client: TestClient, user_id_with_child_access: str, child_ou: str
    ):
        dto = WorkerCreateDto(
            fio="Test",
            drivers_license="123456789",
            active=True,
            organization_unit_id=child_ou,
        )

        result = await client.post(
            "/workers",
            data=dto.json(),
            headers={"X-User-Id": user_id_with_child_access},
        )

        assert result.status_code == 201

        result = await client.post(
            "/workers",
            data=dto.json(),
            headers={"X-User-Id": user_id_with_child_access},
        )

        assert result.status_code == 422
