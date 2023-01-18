import pytest
from async_asgi_testclient import TestClient

from tests.helpers import create_outlet


class TestOutletCreate:
    @pytest.mark.asyncio
    async def test_with_root_access_can_create_outlet_for_root_child(
        self, client: TestClient, user_id_with_root_access: str, child_ou: str
    ):
        result = await create_outlet(client, child_ou, user_id_with_root_access)

        assert result.status_code == 201

    @pytest.mark.asyncio
    async def test_without_root_access_can_not_create_outlet_for_root_child(
        self, client: TestClient, other_child_ou: str, user_id_with_child_access: str
    ):
        result = await create_outlet(client, other_child_ou, user_id_with_child_access)

        assert result.status_code == 403

    @pytest.mark.asyncio
    async def test_with_child_access_can_create_outlet_for_child(
        self, client: TestClient, child_ou: str, user_id_with_child_access: str
    ):
        result = await create_outlet(client, child_ou, user_id_with_child_access)

        assert result.status_code == 201

    @pytest.mark.asyncio
    async def test_with_child_access_can_create_outlet_for_child_of_child(
        self, client: TestClient, user_id_with_child_access: str, child_of_child_ou: str
    ):
        result = await create_outlet(
            client, child_of_child_ou, user_id_with_child_access
        )

        assert result.status_code == 201
