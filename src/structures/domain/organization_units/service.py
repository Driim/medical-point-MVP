import logging

from fastapi import Depends, Request

from src.common.context.context import get_request
from src.common.exceptions import NotImplementedException
from src.common.models import PaginationQueryParams
from src.common.utils.update_model import update_model_by_dto
from src.structures.dal.ou_repository import OrganizationUnitsRepository
from src.structures.domain.organization_units.exceptions import (
    OrganizationUnitNotFound,
    ReadAccessException,
    WriteAccessException,
)
from src.structures.domain.users import UserService

from .models import (
    OrganizationUnit,
    OrganizationUnitCreateDto,
    OrganizationUnitFindDto,
    OrganizationUnitPaginated,
    OrganizationUnitUpdateDto,
)

logger = logging.getLogger(__name__)


class OrganizationUnitService:
    repository: OrganizationUnitsRepository
    user_service: UserService
    repository: OrganizationUnitsRepository

    def __init__(
        self,
        user_service: UserService = Depends(UserService),
        request: Request = Depends(get_request),
        repository: OrganizationUnitsRepository = Depends(OrganizationUnitsRepository),
    ) -> None:
        self.user_service = user_service
        self.request = request
        self.repository = repository

    async def _get_by_id(self, id: str) -> OrganizationUnit:
        ou = await self.repository.get_by_id(id)

        if not ou:
            raise OrganizationUnitNotFound(id)

        return ou

    async def create(
        self,
        dto: OrganizationUnitCreateDto,
        user_id: str,
    ) -> OrganizationUnit:
        print(self.request.state)
        # TODO: remove hardcode, use env
        parent_organization_id: str = (
            dto.parent_organization_unit
            if dto.parent_organization_unit
            # else "c1c83be4-9d4e-4f36-af75-f81507bb7b91"
            else "33b8b452-00cf-42f7-8f4b-ce867c68b8c1"
        )
        if not await self.user_service.have_write_access(
            user_id,
            parent_organization_id,
        ):
            raise WriteAccessException(user_id, parent_organization_id)

        dto.parent_organization_unit = None
        return await self.repository.create(dto, parent_organization_id)

    async def update(
        self,
        id: str,
        dto: OrganizationUnitUpdateDto,
        user_id: str,
    ) -> OrganizationUnit:
        if not await self.user_service.have_write_access(user_id, id):
            raise WriteAccessException(user_id, id)

        ou = await self._get_by_id(id)

        update_model_by_dto(ou, dto.dict())

        return await self.repository.save(ou)

    async def delete(self, id: str, user_id: str) -> None:
        if not await self.user_service.have_write_access(user_id, id):
            raise WriteAccessException(user_id, id)

        ou = await self._get_by_id(id)

        return await self.repository.delete(ou)

    async def get_by_id(self, id: str, user_id: str) -> OrganizationUnit:
        if not await self.user_service.have_read_access(user_id, id):
            raise ReadAccessException(user_id, id)

        return await self._get_by_id(id)

    async def find(
        self,
        dto: OrganizationUnitFindDto,
        pagination: PaginationQueryParams,
        user_id: str,
    ) -> OrganizationUnitPaginated:
        # TODO: limit search by user access rules
        # TODO: if dto has child_of, check access rules and limit request to child_of
        available_ou = await self.user_service.get_available_organization_units(user_id)

        return await self.repository.find(dto, available_ou, pagination)

    async def activate(self, id: str, user_id: str) -> OrganizationUnit:
        if not await self.user_service.have_write_access(user_id, id):
            raise WriteAccessException(user_id, id)

        ou = await self._get_by_id(id)

        ou.active = True

        return await self.repository.save(ou)

    async def deactivate(self, id: str, user_id: str) -> OrganizationUnit:
        if not await self.user_service.have_write_access(user_id, id):
            raise WriteAccessException(user_id, id)

        ou = await self._get_by_id(id)

        ou.active = False

        return await self.repository.save(ou)

    async def change_parent(
        self,
        id: str,
        new_parent: int,
        user_id: str,
    ) -> OrganizationUnit:
        if not await self.user_service.have_write_access(user_id, id):
            raise WriteAccessException(user_id, id)

        if not self.user_service.have_write_access(user_id, new_parent):
            raise WriteAccessException(user_id, new_parent)

        # TODO: change parent operation or something
        raise NotImplementedException()
