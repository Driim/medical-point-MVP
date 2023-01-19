# flake8: noqa: C812
import logging

import pytest
import pytest_asyncio
from async_asgi_testclient import TestClient
from neo4j import GraphDatabase

from src.structures.application import initialize_application
from src.structures.configuration import Configuration
from src.structures.domain.users.models import UserCreateDto
from tests.helpers import create_organization, create_outlet, create_worker

logger = logging.getLogger(__name__)

configuration = Configuration()
driver = GraphDatabase.driver(
    configuration.neo4j.uri,
    auth=(configuration.neo4j.user, configuration.neo4j.password),
)


@pytest_asyncio.fixture
async def client() -> TestClient:
    host, port = "127.0.0.1", "5555"
    scope = {"client": (host, port)}

    app = initialize_application(configuration)

    async with TestClient(app, scope=scope) as client:
        logger.warning(client)
        yield client


@pytest.fixture(autouse=True)
def setup_and_cleanup():
    logger.warning("Setting up env")
    with driver.session() as session:
        session.run(
            f'CREATE (ou:RootOrganizationUnit {{ id: "{configuration.root_ou}" }})'
        )

        yield

        session.run("MATCH (n) OPTIONAL MATCH (n)-[r]-() DETACH DELETE n,r")


def pytest_configure(config):
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """
    logger.warning("Before ALL configuration")
    with driver.session() as session:
        session.run("MATCH (n) OPTIONAL MATCH (n)-[r]-() DETACH DELETE n,r")

        logger.info(configuration.root_ou)

        session.run(
            f'CREATE (ou:RootOrganizationUnit {{ id: "{configuration.root_ou}" }})'
        )

        session.run(
            "CREATE CONSTRAINT ou_id_unique IF NOT EXISTS FOR (ou:OrganizationUnit) REQUIRE ou.id IS UNIQUE"
        )
        session.run(
            "CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE"
        )
        session.run(
            "CREATE CONSTRAINT outlet_id_unique IF NOT EXISTS FOR (o:Outlet) REQUIRE o.id IS UNIQUE"
        )
        session.run(
            "CREATE CONSTRAINT device_id_unique IF NOT EXISTS FOR (d:Device) REQUIRE d.id IS UNIQUE"
        )
        session.run(
            "CREATE CONSTRAINT worker_id_unique IF NOT EXISTS FOR (w:Worker) REQUIRE w.id IS UNIQUE"
        )


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    logger.warning("Before ALL session start")


def pytest_sessionfinish(session, exitstatus):
    """
    Called after whole test run finished, right before
    returning the exit status to the system.
    """
    logger.warning("Before ALL session finish")
    driver.close()


def pytest_unconfigure(config):
    """
    called before test process is exited.
    """
    logger.warning("Before ALL unconfigure")


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


@pytest_asyncio.fixture
async def child_ou_outlet(
    client: TestClient, child_ou: str, user_id_with_root_access: str
) -> str:
    result = await create_outlet(client, child_ou, user_id_with_root_access)

    yield result.json()["id"]


@pytest_asyncio.fixture
async def other_child_ou_outlet(
    client: TestClient, other_child_ou: str, user_id_with_root_access: str
) -> str:
    result = await create_outlet(client, other_child_ou, user_id_with_root_access)

    yield result.json()["id"]


@pytest_asyncio.fixture
async def child_of_child_ou_outlet(
    client: TestClient, child_of_child_ou: str, user_id_with_root_access: str
) -> str:
    result = await create_outlet(client, child_of_child_ou, user_id_with_root_access)

    yield result.json()["id"]


@pytest_asyncio.fixture
async def child_ou_worker(
    client: TestClient, child_ou: str, user_id_with_root_access: str
) -> str:
    result = await create_worker(client, child_ou, user_id_with_root_access)

    yield result.json()["id"]


@pytest_asyncio.fixture
async def other_child_ou_worker(
    client: TestClient, other_child_ou: str, user_id_with_root_access: str
) -> str:
    result = await create_worker(client, other_child_ou, user_id_with_root_access)

    yield result.json()["id"]


@pytest_asyncio.fixture
async def child_of_child_ou_worker(
    client: TestClient, child_of_child_ou: str, user_id_with_root_access: str
) -> str:
    result = await create_worker(client, child_of_child_ou, user_id_with_root_access)

    yield result.json()["id"]
