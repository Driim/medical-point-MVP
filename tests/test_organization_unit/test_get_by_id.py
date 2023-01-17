import logging

import pytest
from async_asgi_testclient import TestClient
from async_asgi_testclient.response import Response

from src.structures.configuration import Configuration

logger = logging.getLogger(__name__)
configuration = Configuration()


async def get_organization(client: TestClient, ou_id: str, user: str) -> Response:
    return await client.get(f"/organization-units/{ou_id}", headers={"X-User-Id": user})


class TestOrganizationUnitGetById:
    @pytest.mark.asyncio
    async def test_with_root_access_can_access_child_of_root(
        self,
        client: TestClient,
        user_id_with_root_access: str,
        child_ou: str,
    ):
        result = await get_organization(client, child_ou, user_id_with_root_access)

        assert result.status_code == 200
        assert set(result.json()["materialized_path"]) == {
            child_ou,
            configuration.root_ou,
        }

    @pytest.mark.asyncio
    async def test_with_root_access_can_access_child_ou(
        self,
        client: TestClient,
        user_id_with_root_access: str,
        child_ou: str,
        child_of_child_ou: str,
    ):
        result = await get_organization(
            client,
            child_of_child_ou,
            user_id_with_root_access,
        )

        assert result.status_code == 200
        assert set(result.json()["materialized_path"]) == {
            child_of_child_ou,
            child_ou,
            configuration.root_ou,
        }

    @pytest.mark.asyncio
    async def test_with_child_access_can_access_child_ou(
        self,
        client: TestClient,
        user_id_with_child_access: str,
        child_ou: str,
    ):
        result = await get_organization(client, child_ou, user_id_with_child_access)

        assert result.status_code == 200

    @pytest.mark.asyncio
    async def test_with_child_access_can_access_child_of_child_ou(
        self,
        client: TestClient,
        user_id_with_child_access: str,
        child_of_child_ou: str,
    ):
        result = await get_organization(
            client,
            child_of_child_ou,
            user_id_with_child_access,
        )

        assert result.status_code == 200

    @pytest.mark.asyncio
    async def test_with_another_child_access_can_not_access_child_ou(
        self,
        client: TestClient,
        user_id_with_child_access: str,
        other_child_ou: str,
    ):
        result = await get_organization(
            client,
            other_child_ou,
            user_id_with_child_access,
        )

        assert result.status_code == 403
