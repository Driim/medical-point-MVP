import logging

import pytest
from async_asgi_testclient import TestClient

from src.structures.configuration import Configuration
from src.structures.domain.organization_units.models import OrganizationUnitFindDto
from tests.helpers import delete_organization, find_organizations

logger = logging.getLogger(__name__)
configuration = Configuration()


class TestOrganizationUnitFind:
    @pytest.mark.asyncio
    async def test_with_root_access_should_show_not_deleted(
        self,
        client: TestClient,
        user_id_with_root_access: str,
        child_of_child_ou: str,
        other_child_ou: str,
    ):
        result = await delete_organization(
            client,
            child_of_child_ou,
            user_id_with_root_access,
        )

        assert result.status_code == 200

        dto = OrganizationUnitFindDto()
        result = await find_organizations(client, dto, user_id_with_root_access)

        assert result.status_code == 200
        logger.warning(f"Deleted company: {child_of_child_ou}")
        logger.warning(result.json()["data"])
        assert result.json()["pagination"]["count"] == 2

    @pytest.mark.asyncio
    async def test_with_child_access_should_show_only_his_branch(
        self,
        client: TestClient,
        user_id_with_child_access: str,
        child_of_child_ou: str,
    ):
        dto = OrganizationUnitFindDto()
        result = await find_organizations(client, dto, user_id_with_child_access)

        assert result.status_code == 200
        logger.warning(result.json())
        assert result.json()["pagination"]["count"] == 2


# TODO: deleting of "middle" ou
