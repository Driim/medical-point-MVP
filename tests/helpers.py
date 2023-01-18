from async_asgi_testclient import TestClient
from async_asgi_testclient.response import Response
from faker import Faker
from faker.providers import company, address

from src.structures.domain.organization_units.models import OrganizationUnitCreateDto, OrganizationUnitUpdateDto, \
    OrganizationUnitFindDto

fake = Faker('ru_RU')
fake.add_provider(company)
fake.add_provider(address)


async def create_organization(
    client: TestClient,
    parent_ou: str | None,
    user_id: str,
) -> Response:
    create_ou_dto = OrganizationUnitCreateDto(
        # TODO: generate random
        name=fake.company(),
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


async def update_organization(client: TestClient, ou_id: str, user_id: str, dto: OrganizationUnitUpdateDto) -> Response:
    return await client.put(f"/organization-units/{ou_id}", headers={"X-User-Id": user_id}, data=dto.json())


async def delete_organization(client: TestClient, ou_id: str, user: str) -> Response:
    return await client.delete(
        f"/organization-units/{ou_id}",
        headers={"X-User-Id": user},
    )


async def find_organizations(client: TestClient, dto: OrganizationUnitFindDto, user_id: str) -> Response:
    return await client.get("/organization-units", headers={"X-User-Id": user_id})
