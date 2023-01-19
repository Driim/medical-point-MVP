import pytest
from async_asgi_testclient import TestClient

from tests.helpers import create_device


class TestWorkerCreate:
    @pytest.mark.asyncio
    async def test_with_root_access_can_create_device_for_root_child(
        self, client: TestClient, user_id_with_root_access: str, child_ou_outlet: str
    ):
        result = await create_device(client, child_ou_outlet, user_id_with_root_access)

        assert result.status_code == 201

    @pytest.mark.asyncio
    async def test_without_root_access_can_not_create_device_for_root_child(
        self,
        client: TestClient,
        other_child_ou_outlet: str,
        user_id_with_child_access: str,
    ):
        result = await create_device(
            client, other_child_ou_outlet, user_id_with_child_access
        )

        assert result.status_code == 403

    @pytest.mark.asyncio
    async def test_with_child_access_can_create_device_for_child(
        self, client: TestClient, child_ou_outlet: str, user_id_with_child_access: str
    ):
        result = await create_device(client, child_ou_outlet, user_id_with_child_access)

        assert result.status_code == 201

    @pytest.mark.asyncio
    async def test_with_child_access_can_create_device_for_child_of_child(
        self,
        client: TestClient,
        user_id_with_child_access: str,
        child_of_child_ou_outlet: str,
    ):
        result = await create_device(
            client, child_of_child_ou_outlet, user_id_with_child_access
        )

        assert result.status_code == 201
