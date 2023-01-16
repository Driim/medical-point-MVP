from pydantic import BaseModel

from src.common.models import Pagination


class DeviceBase(BaseModel):
    id: str
    license: str
    active: bool
    outlet_id: str


class Device(DeviceBase):
    materialized_path: list[str]


class DeviceCreateDto(BaseModel):
    license: str
    active: bool
    outlet_id: str


class DeviceUpdateDto(BaseModel):
    license: str | None


class DeviceFindDto(BaseModel):
    child_of_organization_unit: str | None
    child_of_outlet: str | None
    active: bool | None


class DevicePaginatedDto(BaseModel):
    pagination: Pagination
    data: list[DeviceBase]
