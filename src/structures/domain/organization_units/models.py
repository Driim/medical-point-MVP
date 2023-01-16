from pydantic import BaseModel

from src.common.models import Pagination


class OrganizationUnitShort(BaseModel):
    id: str
    name: str
    inn: int
    kpp: int
    active: bool
    filler: str  # field to make one record 100 KB long


class OrganizationUnitBase(OrganizationUnitShort):
    parent_organization_unit: str  # TODO: get rid of that later


class OrganizationUnit(OrganizationUnitBase):
    materialized_path: list[str]


class OrganizationUnitCreateDto(BaseModel):
    parent_organization_unit: str | None
    name: str
    inn: int
    kpp: int
    legal_address: str
    ogrn: int
    filler: str  # field to make one record 100 KB long


class OrganizationUnitUpdateDto(BaseModel):
    name: str | None
    inn: int | None
    kpp: int | None
    legal_address: str | None
    ogrn: int | None
    filler: str  # field to make one record 100 KB long


class OrganizationUnitFindDto(BaseModel):
    active: bool | None
    child_of: str | None


class OrganizationUnitPaginated(BaseModel):
    pagination: Pagination
    data: list[OrganizationUnitShort]
