import logging

import pytest
from async_asgi_testclient import TestClient

from src.structures.configuration import Configuration
from tests.helpers import create_organization

logger = logging.getLogger(__name__)
configuration = Configuration()


class TestOrganizationUnitCreate:
    @classmethod
    def setup_class(cls):
        logger.warning("starting class: {} execution".format(cls.__name__))

    @classmethod
    def teardown_class(cls):
        logger.warning("starting class: {} execution".format(cls.__name__))

    def setup_method(self, method):
        logger.warning("starting execution of tc: {}".format(method.__name__))

    def teardown_method(self, method):
        logger.warning("starting execution of tc: {}".format(method.__name__))

    @pytest.mark.asyncio
    async def test_with_root_access_can_create_ou_with_parent_root(
        self,
        client: TestClient,
        user_id_with_root_access: str,
    ):
        result = await create_organization(client, None, user_id_with_root_access)

        assert result.status_code == 201

    @pytest.mark.asyncio
    async def test_without_root_access_can_not_create_ou_with_parent_root(
        self,
        client: TestClient,
        user_id_with_child_access: str,
    ):
        result = await create_organization(client, None, user_id_with_child_access)

        assert result.status_code == 403

    @pytest.mark.asyncio
    async def test_with_access_to_other_branch_can_not_create_ou(
        self,
        client: TestClient,
        user_id_with_child_access: str,
        other_child_ou: str,
    ):
        result = await create_organization(
            client,
            other_child_ou,
            user_id_with_child_access,
        )

        assert result.status_code == 403

    @pytest.mark.asyncio
    async def test_with_access_to_ou_can_create_child_ou(
        self,
        client: TestClient,
        user_id_with_child_access: str,
        child_ou: str,
    ):
        result = await create_organization(client, child_ou, user_id_with_child_access)

        assert result.status_code == 201

    @pytest.mark.asyncio
    async def test_with_access_to_ou_can_create_child_to_child_of_ou(
        self,
        client: TestClient,
        user_id_with_child_access: str,
        child_ou: str,
    ):
        result = await create_organization(client, child_ou, user_id_with_child_access)
        result = await create_organization(
            client,
            result.json()["id"],
            user_id_with_child_access,
        )

        assert result.status_code == 201
