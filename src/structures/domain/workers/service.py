import logging

from fastapi import Depends, Request

from src.common.context.context import get_request
from src.common.models import PaginationQueryParams
from src.common.utils import update_model_by_dto
from src.structures.dal.ou_repository import OrganizationUnitsRepository
from src.structures.dal.workers_repository import WorkersRepository
from src.structures.domain.users import UserService
from src.structures.domain.users.exceptions import (
    ReadAccessException,
    WriteAccessException,
)
from src.structures.domain.workers.exceptions import WorkerNotFound
from src.structures.domain.workers.models import (
    Worker,
    WorkerBase,
    WorkerCreateDto,
    WorkerFindDto,
    WorkerPaginatedDto,
    WorkerUpdateDto,
)

logger = logging.getLogger(__name__)


class WorkerService:
    def __init__(
        self,
        user_service: UserService = Depends(UserService),
        repository: WorkersRepository = Depends(WorkersRepository),
        organization_unit_repo: OrganizationUnitsRepository = Depends(
            OrganizationUnitsRepository,
        ),
        request: Request = Depends(get_request),
    ) -> None:
        self._user_service = user_service
        self._repository = repository
        self._org_unit_repo = organization_unit_repo
        self._request = request

    async def _get_by_id(self, worker_id: str) -> WorkerBase:
        worker = await self._repository.get_by_id(worker_id)

        if not worker:
            raise WorkerNotFound(worker_id)

        return worker

    async def _get_by_id_access_right_checked(
        self,
        worker_id: str,
        user_id: str,
        access: str,
    ) -> WorkerBase:
        worker = await self._get_by_id(worker_id)

        if access == "WRITE":
            if not await self._user_service.have_write_access(
                user_id,
                worker.organization_unit_id,
            ):
                raise WriteAccessException(user_id, worker.organization_unit_id)
        else:
            if not await self._user_service.have_read_access(
                user_id,
                worker.organization_unit_id,
            ):
                raise ReadAccessException(user_id, worker.organization_unit_id)

        return worker

    async def _base_to_worker(self, base: WorkerBase) -> Worker:
        ou_path = await self._org_unit_repo.path_to_organization_unit(
            base.organization_unit_id,
            self._request.app.state.ROOT_OU,
        )
        return Worker(materialized_path=ou_path, **base.dict())

    async def create(self, dto: WorkerCreateDto, user_id: str) -> Worker:
        if not await self._user_service.have_write_access(
            user_id,
            dto.organization_unit_id,
        ):
            raise WriteAccessException(user_id, dto.organization_unit_id)

        worker = await self._repository.create(dto)
        return await self._base_to_worker(worker)

    async def update(
        self,
        worker_id: str,
        dto: WorkerUpdateDto,
        user_id: str,
    ) -> Worker:
        worker = await self._get_by_id_access_right_checked(worker_id, user_id, "WRITE")

        update_model_by_dto(worker, dto.dict())

        worker = await self._repository.save(worker)
        return await self._base_to_worker(worker)

    async def delete(self, worker_id: str, user_id: str) -> None:
        worker = await self._get_by_id_access_right_checked(worker_id, user_id, "WRITE")

        return await self._repository.delete(worker)

    async def get_by_id(self, worker_id: str, user_id: str) -> Worker:
        worker = await self._get_by_id_access_right_checked(worker_id, user_id, "READ")

        return await self._base_to_worker(worker)

    async def find(
        self,
        dto: WorkerFindDto,
        pagination: PaginationQueryParams,
        user_id: str,
    ) -> WorkerPaginatedDto:
        available_ou = None
        if dto.child_of:
            if await self._user_service.have_read_access(user_id, dto.child_of):
                available_ou = [dto.child_of]
            else:
                raise ReadAccessException(user_id, dto.child_of)
        else:
            available_ou = await self._user_service.get_available_organization_units(
                user_id,
            )

        return await self._repository.find(dto, available_ou, pagination)

    async def activate(self, worker_id: str, user_id: str) -> Worker:
        worker = await self._get_by_id_access_right_checked(worker_id, user_id, "WRITE")

        worker.active = True
        worker = await self._repository.save(worker)
        return await self._base_to_worker(worker)

    async def deactivate(self, worker_id: str, user_id: str) -> Worker:
        worker = await self._get_by_id_access_right_checked(worker_id, user_id, "WRITE")

        worker.active = False
        worker = await self._repository.save(worker)
        return await self._base_to_worker(worker)

    async def change_parent(
        self,
        worker_id: str,
        new_parent: str,
        user_id: str,
    ) -> Worker:
        worker = await self._get_by_id_access_right_checked(worker_id, user_id, "WRITE")

        if not await self._user_service.have_write_access(user_id, new_parent):
            raise WriteAccessException(user_id, new_parent)

        worker = await self._repository.change_parent_ou(worker, new_parent)
        return await self._base_to_worker(worker)
