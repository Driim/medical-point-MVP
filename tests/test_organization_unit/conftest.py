import pytest_asyncio
from async_asgi_testclient import TestClient

from src.structures.configuration import Configuration
from src.structures.domain.users.models import UserCreateDto
from tests.helpers import create_organization

configuration = Configuration()


@pytest_asyncio.fixture
async def user_id_with_root_access(client: TestClient) -> str:
    root_user_dto = UserCreateDto(
        name="root_user",
        read=[configuration.root_ou],
        write=[configuration.root_ou],
    )

    result = await client.post("/users", data=root_user_dto.json())
    yield result.json()["id"]


@pytest_asyncio.fixture
async def child_ou(client: TestClient, user_id_with_root_access: str) -> str:
    result = await create_organization(client, None, user_id_with_root_access)

    yield result.json()["id"]


@pytest_asyncio.fixture
async def child_of_child_ou(
    client: TestClient,
    user_id_with_root_access: str,
    child_ou: str,
) -> str:
    result = await create_organization(client, child_ou, user_id_with_root_access)

    yield result.json()["id"]


@pytest_asyncio.fixture
async def user_id_with_child_access(client: TestClient, child_ou: str) -> str:
    child_user_dto = UserCreateDto(
        name="child_user",
        read=[child_ou],
        write=[child_ou],
    )

    result = await client.post("/users", data=child_user_dto.json())
    yield result.json()["id"]


@pytest_asyncio.fixture
async def other_child_ou(client: TestClient, user_id_with_root_access: str) -> str:
    result = await create_organization(client, None, user_id_with_root_access)

    yield result.json()["id"]
