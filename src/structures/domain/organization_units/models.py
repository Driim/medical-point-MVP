from typing import Dict

from pydantic import BaseModel

from src.common.models import Pagination


class OrganizationUnit(BaseModel):
    id: str
    name: str
    inn: int
    kpp: int
    legal_address: str
    ognr: int
    active: bool
    contacts: Dict[str, str] | None  # Contacts with details
    contracts: list[str] | None  # ID of contracts


class OrganizationUnitCreateDto(BaseModel):
    parent_organization_unit: str | None
    name: str
    inn: int
    kpp: int
    legal_address: str
    ognr: int
    contacts: Dict[str, str] | None
    contracts: list[str] | None


class OrganizationUnitUpdateDto(BaseModel):
    name: str | None
    inn: int | None
    kpp: int | None
    legal_address: str | None
    ognr: int | None
    contacts: Dict[str, str] | None
    contracts: list[str] | None


class OrganizationUnitFindDto(BaseModel):
    active: bool | None
    child_of: str | None


class OrganizationUnitPaginated(BaseModel):
    pagination: Pagination
    data: list[OrganizationUnit]
