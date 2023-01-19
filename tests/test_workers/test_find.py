import logging

import pytest
from async_asgi_testclient import TestClient
from async_asgi_testclient.response import Response

from src.structures.domain.workers.models import WorkerFindDto
from tests.test_workers.test_delete import delete_worker

logger = logging.getLogger(__name__)


async def find_workers(
    client: TestClient, dto: WorkerFindDto, user_id: str
) -> Response:
    # FIXME: use dto
    return await client.get("/workers", headers={"X-User-Id": user_id})


class TestOutletFind:
    @pytest.mark.asyncio
    async def test_with_root_access_should_show_not_deleted(
        self,
        client: TestClient,
        user_id_with_root_access: str,
        child_of_child_ou_worker: str,
        child_ou_worker: str,
        other_child_ou_worker: str,
    ):
        result = await delete_worker(
            client,
            child_of_child_ou_worker,
            user_id_with_root_access,
        )

        assert result.status_code == 200

        dto = WorkerFindDto()
        result = await find_workers(client, dto, user_id_with_root_access)

        assert result.status_code == 200
        logger.warning(f"Deleted outlet: {child_of_child_ou_worker}")
        logger.warning(result.json()["data"])
        assert result.json()["pagination"]["count"] == 2

    @pytest.mark.asyncio
    async def test_with_child_access_should_show_only_his_branch(
        self,
        client: TestClient,
        user_id_with_child_access: str,
        child_ou_worker: str,
        child_of_child_ou_worker: str,
        other_child_ou_worker: str,
    ):
        dto = WorkerFindDto()
        result = await find_workers(client, dto, user_id_with_child_access)

        assert result.status_code == 200
        logger.warning(result.json())
        assert result.json()["pagination"]["count"] == 2
        # TODO: check ids
