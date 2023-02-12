from pydantic import BaseModel

from src.common.models import Pagination


# TODO: make extended version for get by ID request
class WorkerBase(BaseModel):
    id: str
    fio: str
    drivers_license: str
    active: bool
    organization_unit_id: str


class Worker(WorkerBase):
    materialized_path: list[str]
    is_active_tree: bool


class WorkerCreateDto(BaseModel):
    fio: str
    drivers_license: str
    active: bool
    organization_unit_id: str


class WorkerUpdateDto(BaseModel):
    fio: str | None
    drivers_license: str | None


class WorkerFindDto(BaseModel):
    child_of: str | None
    active: bool | None


class WorkerPaginatedDto(BaseModel):
    pagination: Pagination
    data: list[WorkerBase]
