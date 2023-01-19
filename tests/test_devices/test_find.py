import logging

import pytest
from async_asgi_testclient import TestClient
from async_asgi_testclient.response import Response

from src.structures.domain.devices.models import DeviceFindDto
from src.structures.domain.outlets.models import OutletFindDto
from tests.test_devices.test_delete import delete_device

logger = logging.getLogger(__name__)


async def find_devices(
    client: TestClient, dto: DeviceFindDto, user_id: str
) -> Response:
    # FIXME: use dto
    return await client.get("/devices", headers={"X-User-Id": user_id})


class TestDeviceFind:
    @pytest.mark.asyncio
    async def test_with_root_access_should_show_not_deleted(
        self,
        client: TestClient,
        user_id_with_root_access: str,
        child_of_child_ou_device: str,
        child_ou_device: str,
        other_child_ou_device: str,
    ):
        result = await delete_device(
            client,
            child_of_child_ou_device,
            user_id_with_root_access,
        )

        assert result.status_code == 200

        dto = DeviceFindDto()
        result = await find_devices(client, dto, user_id_with_root_access)

        assert result.status_code == 200
        logger.warning(f"Deleted outlet: {child_of_child_ou_device}")
        logger.warning(result.json()["data"])
        assert result.json()["pagination"]["count"] == 2

    @pytest.mark.asyncio
    async def test_with_child_access_should_show_only_his_branch(
        self,
        client: TestClient,
        user_id_with_child_access: str,
        child_ou_device: str,
        child_of_child_ou_device: str,
        other_child_ou_device: str,
    ):
        dto = OutletFindDto()
        result = await find_devices(client, dto, user_id_with_child_access)

        assert result.status_code == 200
        logger.warning(result.json())
        assert result.json()["pagination"]["count"] == 2
        # TODO: check ids
