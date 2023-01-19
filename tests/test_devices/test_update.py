import pytest
from async_asgi_testclient import TestClient
from async_asgi_testclient.response import Response

from src.structures.domain.devices.models import DeviceUpdateDto


async def update_device(
    client: TestClient, device_id: str, user_id: str, dto: DeviceUpdateDto
) -> Response:
    return await client.put(
        f"/devices/{device_id}", headers={"X-User-Id": user_id}, data=dto.json()
    )


class TestDeviceUpdate:
    @pytest.mark.asyncio
    async def test_with_root_access_can_update_root_child(
        self, client: TestClient, child_ou_device: str, user_id_with_root_access: str
    ):
        dto = DeviceUpdateDto(license="New Name")
        result = await update_device(
            client, child_ou_device, user_id_with_root_access, dto
        )

        assert result.status_code == 200
        assert result.json()["license"] == "New Name"

    @pytest.mark.asyncio
    async def test_without_root_access_can_not_update_root_child(
        self,
        client: TestClient,
        user_id_with_child_access: str,
        other_child_ou_device: str,
    ):
        dto = DeviceUpdateDto(license="New Name")
        result = await update_device(
            client, other_child_ou_device, user_id_with_child_access, dto
        )

        assert result.status_code == 403

    @pytest.mark.asyncio
    async def test_with_child_access_can_update_device_for_child(
        self, client: TestClient, user_id_with_child_access: str, child_ou_device: str
    ):
        dto = DeviceUpdateDto(license="New Name")
        result = await update_device(
            client, child_ou_device, user_id_with_child_access, dto
        )

        assert result.status_code == 200
        assert result.json()["license"] == "New Name"

    @pytest.mark.asyncio
    async def test_with_child_access_can_update_device_for_child_of_child(
        self,
        client: TestClient,
        user_id_with_child_access: str,
        child_of_child_ou_device: str,
    ):
        dto = DeviceUpdateDto(license="New Name")
        result = await update_device(
            client, child_of_child_ou_device, user_id_with_child_access, dto
        )

        assert result.status_code == 200
        assert result.json()["license"] == "New Name"
