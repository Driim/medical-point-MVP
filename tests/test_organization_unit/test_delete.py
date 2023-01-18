import logging

import pytest
from async_asgi_testclient import TestClient

from src.structures.configuration import Configuration
from tests.helpers import create_organization, delete_organization

logger = logging.getLogger(__name__)
configuration = Configuration()


async def is_deleted(client: TestClient, ou_id: str, user: str) -> bool:
    result = await client.get(
        f"/organization-units/{ou_id}",
        headers={"X-User-Id": user},
    )

    return result.status_code == 404


class TestOrganizationUnitDelete:
    @pytest.mark.asyncio
    async def test_without_access_can_not_delete_ou(
        self,
        client: TestClient,
        user_id_with_child_access: str,
        other_child_ou: str,
    ):
        result = await delete_organization(
            client,
            other_child_ou,
            user_id_with_child_access,
        )

        assert result.status_code == 403

    @pytest.mark.asyncio
    async def test_with_access_to_child_ou_can_delete_child_ou(
        self,
        client: TestClient,
        user_id_with_child_access: str,
        child_ou: str,
    ):
        result = await delete_organization(client, child_ou, user_id_with_child_access)

        assert result.status_code == 200
        assert await is_deleted(client, child_ou, user_id_with_child_access)

    @pytest.mark.asyncio
    async def test_with_root_access_can_delete_child_ou(
        self,
        client: TestClient,
        user_id_with_root_access: str,
        child_ou: str,
    ):
        result = await delete_organization(client, child_ou, user_id_with_root_access)

        assert result.status_code == 200
        assert await is_deleted(client, child_ou, user_id_with_root_access)

    @pytest.mark.asyncio
    async def test_with_root_access_can_delete_child_of_child_ou(
        self,
        client: TestClient,
        user_id_with_root_access: str,
        child_ou: str,
    ):
        result = await create_organization(client, child_ou, user_id_with_root_access)
        child_of_child_id = result.json()["id"]

        result = await delete_organization(
            client,
            child_of_child_id,
            user_id_with_root_access,
        )

        assert result.status_code == 200
        assert await is_deleted(client, child_of_child_id, user_id_with_root_access)
