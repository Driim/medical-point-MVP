import pytest
from async_asgi_testclient import TestClient
from async_asgi_testclient.response import Response

from src.structures.domain.outlets.models import OutletUpdateDto


async def update_outlet(
    client: TestClient, outlet_id: str, user_id: str, dto: OutletUpdateDto
) -> Response:
    return await client.put(
        f"/outlets/{outlet_id}", headers={"X-User-Id": user_id}, data=dto.json()
    )


class TestOutletUpdate:
    @pytest.mark.asyncio
    async def test_with_root_access_can_update_root_child(
        self, client: TestClient, child_ou_outlet: str, user_id_with_root_access: str
    ):
        dto = OutletUpdateDto(name="New Name")
        result = await update_outlet(
            client, child_ou_outlet, user_id_with_root_access, dto
        )

        assert result.status_code == 200
        assert result.json()["name"] == "New Name"

    @pytest.mark.asyncio
    async def test_without_root_access_can_not_update_root_child(
        self,
        client: TestClient,
        user_id_with_child_access: str,
        other_child_ou_outlet: str,
    ):
        dto = OutletUpdateDto(name="New Name")
        result = await update_outlet(
            client, other_child_ou_outlet, user_id_with_child_access, dto
        )

        assert result.status_code == 403

    @pytest.mark.asyncio
    async def test_with_child_access_can_update_outlet_for_child(
        self, client: TestClient, user_id_with_child_access: str, child_ou_outlet: str
    ):
        dto = OutletUpdateDto(name="New Name")
        result = await update_outlet(
            client, child_ou_outlet, user_id_with_child_access, dto
        )

        assert result.status_code == 200
        assert result.json()["name"] == "New Name"

    @pytest.mark.asyncio
    async def test_with_child_access_can_update_outlet_for_child_of_child(
        self,
        client: TestClient,
        user_id_with_child_access: str,
        child_of_child_ou_outlet: str,
    ):
        dto = OutletUpdateDto(name="New Name")
        result = await update_outlet(
            client, child_of_child_ou_outlet, user_id_with_child_access, dto
        )

        assert result.status_code == 200
        assert result.json()["name"] == "New Name"
