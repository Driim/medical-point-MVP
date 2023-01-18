import pytest
from async_asgi_testclient import TestClient

from tests.helpers import delete_outlet


async def is_deleted(client: TestClient, outlet_id: str, user: str) -> bool:
    result = await client.get(
        f"/outlets/{outlet_id}",
        headers={"X-User-Id": user},
    )

    return result.status_code == 404


class TestOutletDelete:
    @pytest.mark.asyncio
    async def test_with_root_access_can_delete_root_child(
        self, client: TestClient, user_id_with_root_access: str, child_ou_outlet: str
    ):
        result = await delete_outlet(client, child_ou_outlet, user_id_with_root_access)

        assert result.status_code == 200
        assert await is_deleted(client, child_ou_outlet, user_id_with_root_access)

    @pytest.mark.asyncio
    async def test_without_root_access_can_not_delete_root_child(
        self,
        client: TestClient,
        user_id_with_child_access: str,
        other_child_ou_outlet: str,
    ):
        result = await delete_outlet(
            client, other_child_ou_outlet, user_id_with_child_access
        )

        assert result.status_code == 403

    @pytest.mark.asyncio
    async def test_with_child_access_can_delete_outlet_for_child(
        self, client: TestClient, user_id_with_child_access: str, child_ou_outlet: str
    ):
        result = await delete_outlet(client, child_ou_outlet, user_id_with_child_access)

        assert result.status_code == 200
        assert await is_deleted(client, child_ou_outlet, user_id_with_child_access)

    @pytest.mark.asyncio
    async def test_with_child_access_can_delete_outlet_for_child_of_child(
        self,
        client: TestClient,
        user_id_with_child_access: str,
        child_of_child_ou_outlet: str,
    ):
        result = await delete_outlet(
            client, child_of_child_ou_outlet, user_id_with_child_access
        )

        assert result.status_code == 200
        assert await is_deleted(
            client, child_of_child_ou_outlet, user_id_with_child_access
        )
