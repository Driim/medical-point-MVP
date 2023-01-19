import logging

import pytest
from async_asgi_testclient import TestClient
from async_asgi_testclient.response import Response

from src.structures.configuration import Configuration

logger = logging.getLogger(__name__)
configuration = Configuration()


async def get_device(client: TestClient, device_id: str, user: str) -> Response:
    return await client.get(f"/devices/{device_id}", headers={"X-User-Id": user})


class TestDeviceGetById:
    @pytest.mark.asyncio
    async def test_with_root_access_can_access_root_child(
        self,
        client: TestClient,
        child_ou_device: str,
        user_id_with_root_access: str,
        child_ou: str,
    ):
        result = await get_device(client, child_ou_device, user_id_with_root_access)

        assert result.status_code == 200
        assert set(result.json()["materialized_path"]) == {
            child_ou,
            configuration.root_ou,
        }

    @pytest.mark.asyncio
    async def test_without_root_access_can_not_access_root_child(
        self,
        client: TestClient,
        user_id_with_child_access: str,
        other_child_ou_device: str,
    ):
        result = await get_device(
            client, other_child_ou_device, user_id_with_child_access
        )

        assert result.status_code == 403

    @pytest.mark.asyncio
    async def test_with_child_access_can_access_device_for_child(
        self,
        client: TestClient,
        user_id_with_child_access: str,
        child_ou_device: str,
        child_ou: str,
    ):
        result = await get_device(client, child_ou_device, user_id_with_child_access)

        assert result.status_code == 200
        assert set(result.json()["materialized_path"]) == {
            child_ou,
            configuration.root_ou,
        }

    @pytest.mark.asyncio
    async def test_with_child_access_can_access_device_for_child_of_child(
        self,
        client: TestClient,
        user_id_with_child_access: str,
        child_of_child_ou_device: str,
        child_ou: str,
        child_of_child_ou: str,
    ):
        result = await get_device(
            client, child_of_child_ou_device, user_id_with_child_access
        )

        assert result.status_code == 200
        assert set(result.json()["materialized_path"]) == {
            child_of_child_ou,
            child_ou,
            configuration.root_ou,
        }
