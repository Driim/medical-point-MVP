from async_asgi_testclient import TestClient
from async_asgi_testclient.response import Response
from faker import Faker
from faker.providers import address, company, person

from src.structures.domain.devices.models import DeviceCreateDto
from src.structures.domain.organization_units.models import (
    OrganizationUnitCreateDto,
    OrganizationUnitFindDto,
    OrganizationUnitUpdateDto,
)
from src.structures.domain.outlets.models import OutletCreateDto
from src.structures.domain.workers.models import WorkerCreateDto

fake = Faker("ru_RU")
fake.add_provider(company)
fake.add_provider(address)

fake_person = Faker("ru_RU")
fake_person.add_provider(address)
fake_person.add_provider(person)

organization_counter = 0
outlet_counter = 0
workers_counter = 0
devices_counter = 0


async def create_organization(
    client: TestClient,
    parent_ou: str | None,
    user_id: str,
) -> Response:
    global organization_counter
    organization_counter += 1
    create_ou_dto = OrganizationUnitCreateDto(
        name=f"{organization_counter}-{fake.company()}",
        inn=fake.businesses_inn(),
        kpp=fake.kpp(),
        legal_address=fake.address(),
        ogrn=fake.businesses_ogrn(),
        filler=fake.text(),
        parent_organization_unit=parent_ou,
    )

    return await client.post(
        "/organization-units",
        data=create_ou_dto.json(),
        headers={"X-User-Id": user_id},
    )


async def update_organization(
    client: TestClient, ou_id: str, user_id: str, dto: OrganizationUnitUpdateDto
) -> Response:
    return await client.put(
        f"/organization-units/{ou_id}", headers={"X-User-Id": user_id}, data=dto.json()
    )


async def delete_organization(client: TestClient, ou_id: str, user: str) -> Response:
    return await client.delete(
        f"/organization-units/{ou_id}",
        headers={"X-User-Id": user},
    )


async def find_organizations(
    client: TestClient, dto: OrganizationUnitFindDto, user_id: str
) -> Response:
    return await client.get("/organization-units", headers={"X-User-Id": user_id})


async def create_outlet(
    client: TestClient, parent_ou: str | None, user_id: str
) -> Response:
    global outlet_counter
    outlet_counter += 1
    dto = OutletCreateDto(
        name=f"{outlet_counter}-{fake.name()}",
        address=fake.address(),
        active=True,
        organization_unit_id=parent_ou,
    )

    return await client.post(
        "/outlets",
        data=dto.json(),
        headers={"X-User-Id": user_id},
    )


async def delete_outlet(client: TestClient, outlet_id: str, user: str) -> Response:
    return await client.delete(
        f"/outlets/{outlet_id}",
        headers={"X-User-Id": user},
    )


async def create_worker(client: TestClient, parent_ou: str, user_id: str) -> Response:
    global workers_counter
    workers_counter += 1
    dto = WorkerCreateDto(
        fio=f"{workers_counter}-{fake_person.name()}",
        drivers_license=fake.businesses_inn(),
        active=True,
        organization_unit_id=parent_ou,
    )

    return await client.post(
        "/workers",
        data=dto.json(),
        headers={"X-User-Id": user_id},
    )


async def create_device(
    client: TestClient, parent_outlet: str, user_id: str
) -> Response:
    global devices_counter
    devices_counter += 1
    dto = DeviceCreateDto(
        license=f"{devices_counter}-{fake.businesses_inn()}",
        active=True,
        outlet_id=parent_outlet,
    )

    return await client.post(
        "/devices",
        data=dto.json(),
        headers={"X-User-Id": user_id},
    )
