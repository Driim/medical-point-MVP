import logging

import pytest
from async_asgi_testclient import TestClient

from src.structures.configuration import Configuration
from src.structures.domain.organization_units.models import OrganizationUnitUpdateDto
from tests.helpers import update_organization

logger = logging.getLogger(__name__)
configuration = Configuration()


class TestOrganizationUnitUpdate:
    @pytest.mark.asyncio
    async def test_with_root_access_can_update_child_of_root(
        self,
        client: TestClient,
        user_id_with_root_access: str,
        child_ou: str,
    ):
        dto = OrganizationUnitUpdateDto(
            name="New name"
        )
        result = await update_organization(client, child_ou, user_id_with_root_access, dto)

        assert result.status_code == 200
        assert result.json()["name"] == "New name"

    @pytest.mark.asyncio
    async def test_without_root_access_can_not_update_child_of_root(
        self,
        client: TestClient,
        other_child_ou: str,
        user_id_with_child_access: str,
    ):
        dto = OrganizationUnitUpdateDto(
            name="New name"
        )
        result = await update_organization(client, other_child_ou, user_id_with_child_access, dto)

        assert result.status_code == 403

    @pytest.mark.asyncio
    async def test_with_child_access_can_update_child(
        self,
        client: TestClient,
        user_id_with_child_access: str,
        child_ou: str,
    ):
        dto = OrganizationUnitUpdateDto(
            name="New name"
        )
        result = await update_organization(client, child_ou, user_id_with_child_access, dto)

        assert result.status_code == 200
        assert result.json()["name"] == "New name"

    @pytest.mark.asyncio
    async def test_with_child_access_can_update_child_of_child(
        self,
        client: TestClient,
        user_id_with_child_access: str,
        child_of_child_ou: str,
    ):
        dto = OrganizationUnitUpdateDto(
            name="New name"
        )
        result = await update_organization(client, child_of_child_ou, user_id_with_child_access, dto)

        assert result.status_code == 200
        assert result.json()["name"] == "New name"
