from pydantic import BaseModel

from src.common.models import Pagination


# TODO: make extended version for get by ID request
class OutletBase(BaseModel):
    id: str
    name: str
    address: str
    active: bool
    organization_unit_id: str


class Outlet(OutletBase):
    materialized_path: list[str]


class OutletCreateDto(BaseModel):
    name: str
    address: str
    active: bool
    organization_unit_id: str


class OutletUpdateDto(BaseModel):
    name: str | None
    address: str | None


class OutletFindDto(BaseModel):
    child_of: str | None
    active: bool | None


class OutletPaginated(BaseModel):
    pagination: Pagination
    data: list[OutletBase]
