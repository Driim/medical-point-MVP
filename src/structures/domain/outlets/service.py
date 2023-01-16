import logging

from fastapi import Depends, Request

from src.common.context.context import get_request
from src.common.models import PaginationQueryParams
from src.common.utils import update_model_by_dto
from src.structures.dal.ou_repository import OrganizationUnitsRepository
from src.structures.dal.outlets_repository import OutletsRepository
from src.structures.domain.outlets.exceptions import OutletNotFound
from src.structures.domain.outlets.models import (
    Outlet,
    OutletBase,
    OutletCreateDto,
    OutletFindDto,
    OutletPaginated,
    OutletUpdateDto,
)
from src.structures.domain.users import UserService
from src.structures.domain.users.exceptions import (
    ReadAccessException,
    WriteAccessException,
)

logger = logging.getLogger(__name__)


class OutletService:
    def __init__(
        self,
        user_service: UserService = Depends(UserService),
        repository: OutletsRepository = Depends(OutletsRepository),
        organization_unit_repo: OrganizationUnitsRepository = Depends(
            OrganizationUnitsRepository,
        ),
        request: Request = Depends(get_request),
    ):
        self._user_service = user_service
        self._repository = repository
        self._org_unit_repo = organization_unit_repo
        self._request = request

    async def _get_by_id(self, outlet_id: str) -> OutletBase:
        outlet = await self._repository.get_by_id(outlet_id)

        if not outlet:
            raise OutletNotFound(outlet_id)

        return outlet

    async def _get_by_id_access_right_checked(
        self,
        outlet_id: str,
        user_id: str,
        access: str,
    ) -> OutletBase:
        outlet = await self._get_by_id(outlet_id)

        if access == "WRITE":
            if not await self._user_service.have_write_access(
                user_id,
                outlet.organization_unit_id,
            ):
                raise WriteAccessException(user_id, outlet.organization_unit_id)
        else:
            if not await self._user_service.have_read_access(
                user_id,
                outlet.organization_unit_id,
            ):
                raise ReadAccessException(user_id, outlet.organization_unit_id)

        return outlet

    async def _base_to_outlet(self, base: OutletBase) -> Outlet:
        ou_path = await self._org_unit_repo.path_to_organization_unit(
            base.organization_unit_id,
            self._request.app.state.ROOT_OU,
        )
        return Outlet(materialized_path=ou_path, **base.dict())

    async def create(self, dto: OutletCreateDto, user_id: str) -> Outlet:
        if not await self._user_service.have_write_access(
            user_id,
            dto.organization_unit_id,
        ):
            raise WriteAccessException(user_id, dto.organization_unit_id)

        outlet = await self._repository.create(dto)
        return await self._base_to_outlet(outlet)

    async def update(
        self,
        outlet_id: str,
        dto: OutletUpdateDto,
        user_id: str,
    ) -> Outlet:
        outlet = await self._get_by_id_access_right_checked(outlet_id, user_id, "WRITE")

        update_model_by_dto(outlet, dto.dict())

        outlet = await self._repository.save(outlet)
        return await self._base_to_outlet(outlet)

    async def delete(self, outlet_id: str, user_id: str) -> None:
        outlet = await self._get_by_id_access_right_checked(outlet_id, user_id, "WRITE")

        # TODO: cascade delete all devices

        return await self._repository.delete(outlet)

    async def get_by_id(self, outlet_id: str, user_id: str) -> Outlet:
        outlet = await self._get_by_id_access_right_checked(outlet_id, user_id, "READ")

        return await self._base_to_outlet(outlet)

    async def find(
        self,
        dto: OutletFindDto,
        pagination: PaginationQueryParams,
        user_id: str,
    ) -> OutletPaginated:
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

    async def activate(self, outlet_id: str, user_id: str) -> Outlet:
        logger.warning("Start active state")
        outlet = await self._get_by_id_access_right_checked(outlet_id, user_id, "WRITE")

        outlet.active = True
        logger.warning("Setup active state")
        outlet = await self._repository.save(outlet)
        logger.warning("Saved new state")
        return await self._base_to_outlet(outlet)

    async def deactivate(self, outlet_id: str, user_id: str) -> Outlet:
        outlet = await self._get_by_id_access_right_checked(outlet_id, user_id, "WRITE")

        outlet.active = False
        outlet = await self._repository.save(outlet)
        return await self._base_to_outlet(outlet)

    async def change_organization(
        self,
        outlet_id: str,
        organization_id: str,
        user_id: str,
    ) -> Outlet:
        outlet = await self._get_by_id_access_right_checked(outlet_id, user_id, "WRITE")

        if not await self._user_service.have_write_access(user_id, organization_id):
            raise WriteAccessException(user_id, organization_id)

        outlet = await self._repository.change_parent_ou(outlet, organization_id)
        return await self._base_to_outlet(outlet)
