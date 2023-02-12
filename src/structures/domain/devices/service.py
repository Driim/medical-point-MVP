import logging

from fastapi import Depends, Request

from src.common.context.context import get_request
from src.common.models import PaginationQueryParams
from src.common.utils import update_model_by_dto
from src.structures.dal.devices_repository import DevicesRepository
from src.structures.dal.ou_repository import OrganizationUnitsRepository
from src.structures.dal.outlets_repository import OutletsRepository
from src.structures.dal.workers_repository import WorkersRepository
from src.structures.domain.devices.exceptions import DeviceNotFound
from src.structures.domain.devices.models import (
    Device,
    DeviceBase,
    DeviceCreateDto,
    DeviceExamForWorker,
    DeviceFindDto,
    DevicePaginatedDto,
    DeviceUpdateDto,
)
from src.structures.domain.users import UserService
from src.structures.domain.users.exceptions import (
    DeviceExamAccessException,
    OutletReadAccessException,
    OutletWriteAccessException,
    ReadAccessException,
)
from src.structures.domain.workers.models import Worker

logger = logging.getLogger(__name__)


class DeviceService:
    def __init__(
        self,
        user_service: UserService = Depends(UserService),
        repository: DevicesRepository = Depends(DevicesRepository),
        organization_unit_repo: OrganizationUnitsRepository = Depends(
            OrganizationUnitsRepository,
        ),
        outlet_repo: OutletsRepository = Depends(OutletsRepository),
        worker_repo: WorkersRepository = Depends(WorkersRepository),
        request: Request = Depends(get_request),
    ):
        self._user_service = user_service
        self._repository = repository
        self._org_unit_repo = organization_unit_repo
        self._outlet_repo = outlet_repo
        self._worker_repo = worker_repo
        self._request = request

    async def _get_by_id(self, device_id: str) -> DeviceBase:
        device = await self._repository.get_by_id(device_id)

        if not device:
            raise DeviceNotFound(device_id)

        return device

    async def _get_by_id_access_right_checked(
        self,
        device_id: str,
        user_id: str,
        access: str,
    ) -> DeviceBase:
        device = await self._get_by_id(device_id)

        if access == "WRITE":
            if not await self._user_service.have_write_access_by_outlet(
                user_id,
                device.outlet_id,
            ):
                raise OutletWriteAccessException(user_id, device.outlet_id)
        else:
            if not await self._user_service.have_read_access_by_outlet(
                user_id,
                device.outlet_id,
            ):
                raise OutletReadAccessException(user_id, device.outlet_id)

        return device

    async def _base_to_device(self, base: DeviceBase) -> Device:
        ou = await self._outlet_repo.get_by_id(base.outlet_id)

        ou_path = await self._org_unit_repo.path_to_organization_unit(
            ou.organization_unit_id,
            self._request.app.state.ROOT_OU,
        )

        is_active_tree = False
        if base.active is True:
            is_active_tree = await self._org_unit_repo.is_in_active_tree(
                ou.organization_unit_id,
                self._request.app.state.ROOT_OU,
            )

        return Device(
            is_active_tree=base.active and is_active_tree,
            materialized_path=ou_path,
            **base.dict()
        )

    async def create(self, dto: DeviceCreateDto, user_id: str) -> Device:
        if not await self._user_service.have_write_access_by_outlet(
            user_id, dto.outlet_id
        ):
            raise OutletWriteAccessException(user_id, dto.outlet_id)

        base = await self._repository.create(dto)
        return await self._base_to_device(base)

    async def update(
        self,
        device_id: str,
        dto: DeviceUpdateDto,
        user_id: str,
    ) -> Device:
        device = await self._get_by_id_access_right_checked(device_id, user_id, "WRITE")

        update_model_by_dto(device, dto.dict())

        base = await self._repository.save(device)
        return await self._base_to_device(base)

    async def delete(self, device_id: str, user_id: str) -> None:
        device = await self._get_by_id_access_right_checked(device_id, user_id, "WRITE")

        return await self._repository.delete(device)

    async def get_by_id(self, device_id: str, user_id: str) -> Device:
        base = await self._get_by_id_access_right_checked(device_id, user_id, "READ")
        return await self._base_to_device(base)

    async def find(
        self,
        dto: DeviceFindDto,
        pagination: PaginationQueryParams,
        user_id: str,
    ) -> DevicePaginatedDto:
        available_ou = None
        if dto.child_of_organization_unit:
            if await self._user_service.have_read_access(
                user_id,
                dto.child_of_organization_unit,
            ):
                available_ou = [dto.child_of_organization_unit]
            else:
                raise ReadAccessException(user_id, dto.child_of_organization_unit)
        else:
            available_ou = await self._user_service.get_available_organization_units(
                user_id,
            )

        available_outlets = None
        if dto.child_of_outlet:
            if await self._user_service.have_read_access_by_outlet(
                user_id,
                dto.child_of_outlet,
            ):
                available_outlets = [dto.child_of_outlet]
            else:
                raise OutletReadAccessException(user_id, dto.child_of_outlet)

        return await self._repository.find(
            dto,
            available_ou,
            available_outlets,
            pagination,
        )

    async def activate(self, device_id: str, user_id: str) -> Device:
        device = await self._get_by_id_access_right_checked(device_id, user_id, "WRITE")
        device.active = True
        base = await self._repository.save(device)
        return await self._base_to_device(base)

    async def deactivate(self, device_id: str, user_id: str) -> Device:
        device = await self._get_by_id_access_right_checked(device_id, user_id, "WRITE")
        device.active = False
        base = await self._repository.save(device)
        return await self._base_to_device(base)

    async def change_outlet(
        self,
        device_id: str,
        new_parent_outlet: str,
        user_id: str,
    ) -> Device:
        device = await self._get_by_id_access_right_checked(device_id, user_id, "WRITE")

        if not await self._user_service.have_write_access_by_outlet(
            user_id,
            new_parent_outlet,
        ):
            raise OutletWriteAccessException(user_id, new_parent_outlet)

        base = await self._repository.change_parent_outlet(device, new_parent_outlet)
        return await self._base_to_device(base)

    async def can_take_exam_on_device(self, device_id: str, worker_id: str):
        can_take_exam = await self._repository.can_take_exam_on_device(device_id, worker_id)
        if not can_take_exam:
            can_take_exam = await self._repository.org_have_agreement(device_id, worker_id)

        if not can_take_exam:
            raise DeviceExamAccessException(worker_id, device_id)

        base_device = await self._get_by_id(device_id)
        device = await self._base_to_device(base_device)

        base_worker = await self._worker_repo.get_by_id(worker_id)
        # copypaste from worker service
        # TODO: can be optimized, second call not needed if same OU
        ou_path = await self._org_unit_repo.path_to_organization_unit(
            base_worker.organization_unit_id,
            self._request.app.state.ROOT_OU,
        )

        is_active_tree = False
        if base_worker.active is True:
            is_active_tree = await self._org_unit_repo.is_in_active_tree(
                base_worker.organization_unit_id,
                self._request.app.state.ROOT_OU,
            )

        worker = Worker(
            is_active_tree=base_worker.active and is_active_tree,
            materialized_path=ou_path,
            **base_worker.dict(),
        )

        return DeviceExamForWorker(worker=worker, device=device)
