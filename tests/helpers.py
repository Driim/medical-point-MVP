from async_asgi_testclient import TestClient
from async_asgi_testclient.response import Response

from src.structures.domain.organization_units.models import OrganizationUnitCreateDto


async def create_organization(
    client: TestClient,
    parent_ou: str | None,
    user_id: str,
) -> Response:
    create_ou_dto = OrganizationUnitCreateDto(
        # TODO: generate random
        name="Test",
        inn=1,
        kpp=2,
        legal_address="Street",
        ogrn=3,
        filler="long str",
        parent_organization_unit=parent_ou,
    )

    return await client.post(
        "/organization-units",
        data=create_ou_dto.json(),
        headers={"X-User-Id": user_id},
    )
