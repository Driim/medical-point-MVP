import logging

import pytest
from async_asgi_testclient import TestClient
from async_asgi_testclient.response import Response

from src.structures.configuration import Configuration

logger = logging.getLogger(__name__)
configuration = Configuration()


async def change_parent_organization(
    client: TestClient, device_id: str, new_parent_id: str, user: str
) -> Response:
    return await client.patch(
        f"/devices/{device_id}/change-outlet/{new_parent_id}",
        headers={"X-User-Id": user},
    )


class TestDeviceChangeParent:
    @pytest.mark.asyncio
    async def test_with_root_access_can_change_parent(
        self,
        client: TestClient,
        user_id_with_root_access: str,
        child_ou_device: str,
        other_child_ou: str,
        other_child_ou_outlet: str,
    ):
        result = await change_parent_organization(
            client, child_ou_device, other_child_ou_outlet, user_id_with_root_access
        )

        assert result.status_code == 200
        assert result.json()["outlet_id"] == other_child_ou_outlet
        assert set(result.json()["materialized_path"]) == {
            other_child_ou,
            configuration.root_ou,
        }
