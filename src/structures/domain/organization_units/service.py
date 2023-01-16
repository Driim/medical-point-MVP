import logging

from fastapi import Depends, Request

from src.common.context.context import get_request
from src.common.models import PaginationQueryParams
from src.common.utils.update_model import update_model_by_dto
from src.structures.dal.ou_repository import OrganizationUnitsRepository
from src.structures.domain.organization_units.exceptions import OrganizationUnitNotFound
from src.structures.domain.users import UserService

from ..users.exceptions import ReadAccessException, WriteAccessException
from .models import (
    OrganizationUnit,
    OrganizationUnitBase,
    OrganizationUnitCreateDto,
    OrganizationUnitFindDto,
    OrganizationUnitPaginated,
    OrganizationUnitUpdateDto,
)

logger = logging.getLogger(__name__)


class OrganizationUnitService:
    def __init__(
        self,
        user_service: UserService = Depends(UserService),
        request: Request = Depends(get_request),
        repository: OrganizationUnitsRepository = Depends(OrganizationUnitsRepository),
    ) -> None:
        self._user_service = user_service
        self.request = request
        self.repository = repository

    async def _base_to_organization_unit(
        self,
        ou: OrganizationUnitBase,
    ) -> OrganizationUnit:
        ou_path = await self.repository.path_to_organization_unit(
            ou.id,
            self.request.app.state.ROOT_OU,
        )

        return OrganizationUnit(materialized_path=ou_path, **ou.dict())

    async def _get_by_id(self, id: str) -> OrganizationUnitBase:
        ou = await self.repository.get_by_id(id)

        if not ou:
            raise OrganizationUnitNotFound(id)

        return ou

    async def _get_by_id_access_right_checked(
        self,
        ou_id: str,
        user_id: str,
        access: str,
    ) -> OrganizationUnitBase:
        ou = await self._get_by_id(ou_id)

        if access == "WRITE":
            if not await self._user_service.have_write_access(user_id, ou.id):
                raise WriteAccessException(user_id, ou.id)
        else:
            if not await self._user_service.have_read_access(user_id, ou.id):
                raise ReadAccessException(user_id, ou.id)

        return ou

    async def create(
        self,
        dto: OrganizationUnitCreateDto,
        user_id: str,
    ) -> OrganizationUnit:
        parent_organization_id: str = (
            dto.parent_organization_unit
            if dto.parent_organization_unit
            else self.request.app.state.ROOT_OU
        )
        if not await self._user_service.have_write_access(
            user_id,
            parent_organization_id,
        ):
            raise WriteAccessException(user_id, parent_organization_id)

        dto.parent_organization_unit = None
        ou = await self.repository.create(dto, parent_organization_id)
        return await self._base_to_organization_unit(ou)

    async def update(
        self,
        id: str,
        dto: OrganizationUnitUpdateDto,
        user_id: str,
    ) -> OrganizationUnit:
        ou = await self._get_by_id_access_right_checked(id, user_id, "WRITE")

        update_model_by_dto(ou, dto.dict())

        ou = await self.repository.save(ou)
        return await self._base_to_organization_unit(ou)

    async def delete(self, id: str, user_id: str) -> None:
        ou = await self._get_by_id_access_right_checked(id, user_id, "WRITE")

        # TODO: delete all child OU also

        return await self.repository.delete(ou)

    async def get_by_id(self, id: str, user_id: str) -> OrganizationUnit:
        ou = await self._get_by_id_access_right_checked(id, user_id, "READ")

        return await self._base_to_organization_unit(ou)

    async def find(
        self,
        dto: OrganizationUnitFindDto,
        pagination: PaginationQueryParams,
        user_id: str,
    ) -> OrganizationUnitPaginated:
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

        return await self.repository.find(dto, available_ou, pagination)

    async def activate(self, id: str, user_id: str) -> OrganizationUnit:
        ou = await self._get_by_id_access_right_checked(id, user_id, "WRITE")

        ou.active = True

        ou = await self.repository.save(ou)
        return await self._base_to_organization_unit(ou)

    async def deactivate(self, id: str, user_id: str) -> OrganizationUnit:
        ou = await self._get_by_id_access_right_checked(id, user_id, "WRITE")

        ou.active = False

        ou = await self.repository.save(ou)
        return await self._base_to_organization_unit(ou)

    async def change_parent(
        self,
        id: str,
        new_parent: str,
        user_id: str,
    ) -> OrganizationUnit:
        ou = await self._get_by_id_access_right_checked(id, user_id, "WRITE")

        if not self._user_service.have_write_access(user_id, new_parent):
            raise WriteAccessException(user_id, new_parent)

        ou = await self.repository.change_parent_ou(ou, new_parent)
        return await self._base_to_organization_unit(ou)
