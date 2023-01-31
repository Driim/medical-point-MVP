import logging

import pytest
from async_asgi_testclient import TestClient
from async_asgi_testclient.response import Response

from src.structures.configuration import Configuration
from tests.helpers import (
    deactivate_device,
    deactivate_organization,
    deactivate_outlet,
    deactivate_worker,
    delete_device,
    delete_organization,
    delete_outlet,
    delete_worker,
)

logger = logging.getLogger(__name__)
configuration = Configuration()


async def get_device_exam(
    client: TestClient, device_id: str, worker_id: str
) -> Response:
    return await client.get(
        f"/devices/{device_id}/exam/{worker_id}",
        headers={"X-User-Id": "do not matters"},
    )


class TestDeviceGetExam:
    @pytest.mark.asyncio
    async def test_worker_on_same_ou_devices_can_take_exam(
        self,
        client: TestClient,
        child_ou_device: str,
        child_ou_worker: str,
    ):
        result = await get_device_exam(client, child_ou_device, child_ou_worker)
        assert result.status_code == 200
        assert set(result.json()["worker"]["materialized_path"]) == set(
            result.json()["device"]["materialized_path"]
        )

    @pytest.mark.asyncio
    async def test_worker_on_other_ou_devices_can_not_take_exam(
        self,
        client: TestClient,
        child_ou_device: str,
        other_child_ou_worker: str,
    ):
        result = await get_device_exam(client, child_ou_device, other_child_ou_worker)
        assert result.status_code == 403

    @pytest.mark.asyncio
    async def test_worker_on_child_of_child_ou_devices_can_not_take_exam(
        self,
        client: TestClient,
        child_ou_device: str,
        child_of_child_ou_worker: str,
    ):
        # TODO: check is it right?
        result = await get_device_exam(
            client, child_ou_device, child_of_child_ou_worker
        )
        assert result.status_code == 403

    @pytest.mark.asyncio
    async def test_worker_with_ou_deleted_can_not_take_exam(
        self,
        client: TestClient,
        child_ou_device: str,
        child_ou_worker: str,
        child_ou: str,
        user_id_with_root_access: str,
    ):
        result = await delete_organization(client, child_ou, user_id_with_root_access)
        assert result.status_code == 200

        result = await get_device_exam(client, child_ou_device, child_ou_worker)
        assert result.status_code == 403

    @pytest.mark.asyncio
    async def test_worker_with_device_deleted_can_not_take_exam(
        self,
        client: TestClient,
        child_ou_device: str,
        child_ou_worker: str,
        user_id_with_root_access: str,
    ):
        result = await delete_device(client, child_ou_device, user_id_with_root_access)
        assert result.status_code == 200

        result = await get_device_exam(client, child_ou_device, child_ou_worker)
        assert result.status_code == 403

    @pytest.mark.asyncio
    async def test_worker_with_worker_deleted_can_not_take_exam(
        self,
        client: TestClient,
        child_ou_device: str,
        child_ou_worker: str,
        user_id_with_root_access: str,
    ):
        result = await delete_worker(client, child_ou_worker, user_id_with_root_access)
        assert result.status_code == 200

        result = await get_device_exam(client, child_ou_device, child_ou_worker)
        assert result.status_code == 403

    @pytest.mark.asyncio
    async def test_worker_with_outlet_deleted_can_not_take_exam(
        self,
        client: TestClient,
        child_ou_device: str,
        child_ou_worker: str,
        child_ou_outlet: str,
        user_id_with_root_access: str,
    ):
        result = await delete_outlet(client, child_ou_outlet, user_id_with_root_access)
        assert result.status_code == 200

        result = await get_device_exam(client, child_ou_device, child_ou_worker)
        assert result.status_code == 403

    @pytest.mark.asyncio
    async def test_worker_with_ou_deactivated_can_not_take_exam(
        self,
        client: TestClient,
        child_ou_device: str,
        child_ou_worker: str,
        child_ou: str,
        user_id_with_root_access: str,
    ):
        result = await deactivate_organization(
            client, child_ou, user_id_with_root_access
        )
        assert result.status_code == 200

        result = await get_device_exam(client, child_ou_device, child_ou_worker)
        assert result.status_code == 403

    @pytest.mark.asyncio
    async def test_worker_with_device_deactivated_can_not_take_exam(
        self,
        client: TestClient,
        child_ou_device: str,
        child_ou_worker: str,
        user_id_with_root_access: str,
    ):
        result = await deactivate_device(
            client, child_ou_device, user_id_with_root_access
        )
        assert result.status_code == 200

        result = await get_device_exam(client, child_ou_device, child_ou_worker)
        assert result.status_code == 403

    @pytest.mark.asyncio
    async def test_worker_with_worker_deactivated_can_not_take_exam(
        self,
        client: TestClient,
        child_ou_device: str,
        child_ou_worker: str,
        user_id_with_root_access: str,
    ):
        result = await deactivate_worker(
            client, child_ou_worker, user_id_with_root_access
        )
        assert result.status_code == 200

        result = await get_device_exam(client, child_ou_device, child_ou_worker)
        assert result.status_code == 403

    @pytest.mark.asyncio
    async def test_worker_with_outlet_deactivated_can_not_take_exam(
        self,
        client: TestClient,
        child_ou_device: str,
        child_ou_worker: str,
        child_ou_outlet: str,
        user_id_with_root_access: str,
    ):
        result = await deactivate_outlet(
            client, child_ou_outlet, user_id_with_root_access
        )
        assert result.status_code == 200

        result = await get_device_exam(client, child_ou_device, child_ou_worker)
        assert result.status_code == 403
