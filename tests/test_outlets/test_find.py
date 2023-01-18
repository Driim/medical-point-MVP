import logging

import pytest
from async_asgi_testclient import TestClient
from async_asgi_testclient.response import Response

from src.structures.domain.outlets.models import OutletFindDto

logger = logging.getLogger(__name__)


async def find_outlets(
    client: TestClient, dto: OutletFindDto, user_id: str
) -> Response:
    # FIXME: use dto
    return await client.get("/outlets", headers={"X-User-Id": user_id})


class TestOutletFind:
    @pytest.mark.asyncio
    @pytest.mark.skip(
        reason="Gives different answer in single and a batch run"
    )  # FIXME: find a reason
    async def test_with_root_access_should_show_not_deleted(self):
        pass

    @pytest.mark.asyncio
    async def test_with_child_access_should_show_only_his_branch(
        self,
        client: TestClient,
        user_id_with_child_access: str,
        child_ou_outlet: str,
        child_of_child_ou_outlet: str,
        other_child_ou_outlet: str,
    ):
        dto = OutletFindDto()
        result = await find_outlets(client, dto, user_id_with_child_access)

        assert result.status_code == 200
        logger.warning(result.json())
        assert result.json()["pagination"]["count"] == 2
        # TODO: check ids
