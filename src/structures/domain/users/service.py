from fastapi import Depends, Request

from src.common.context.context import get_request
from src.structures.dal.users_repository import UsersRepository
from src.structures.domain.users.exceptions import UserNotFound
from src.structures.domain.users.models import User, UserCreateDto


class UserService:
    def __init__(
        self,
        repository: UsersRepository = Depends(UsersRepository),
        request: Request = Depends(get_request),
    ) -> None:
        self.repository = repository
        self.request = request

    async def _get_by_id(self, id: str) -> User:
        user = await self.repository.get_by_id(id)

        if not user:
            raise UserNotFound(id)

        return user

    async def get_user_by_id(self, user_id: str) -> User:
        return await self._get_by_id(user_id)

    async def have_read_access(self, user_id: str, organization_id: str) -> bool:
        return await self.repository.has_access_right(
            user_id,
            organization_id,
            self.request.app.state.ROOT_OU,
            "READ_ACCESS",
        )

    async def have_write_access(self, user_id: str, organization_id: str) -> bool:
        return await self.repository.has_access_right(
            user_id,
            organization_id,
            self.request.app.state.ROOT_OU,
            "WRITE_ACCESS",
        )

    async def have_write_access_by_outlet(self, user_id: str, outlet_id: str) -> bool:
        return await self.repository.have_write_access_by_outlet(
            user_id,
            outlet_id,
            self.request.app.state.ROOT_OU,
            "WRITE_ACCESS",
        )

    async def have_read_access_by_outlet(self, user_id, outlet_id: str) -> bool:
        return await self.repository.have_write_access_by_outlet(
            user_id,
            outlet_id,
            self.request.app.state.ROOT_OU,
            "READ_ACCESS",
        )

    async def get_available_organization_units(self, user_id: str) -> list[str]:
        result = set()

        user = await self._get_by_id(user_id)

        for ou in user.read:
            result.add(ou)

        for ou in user.write:
            result.add(ou)

        return list(result)

    async def create(self, dto: UserCreateDto) -> User:
        return await self.repository.create(dto)

    async def delete(self, user_id: str) -> None:
        user = await self._get_by_id(user_id)

        await self.repository.delete(user)

    async def add_read_access(self, user_id: str, ou_ids: list[str]) -> User:
        user = await self._get_by_id(user_id)

        return await self.repository.add_relation(user, "READ_ACCESS", ou_ids)

    async def add_write_access(self, user_id: str, ou_ids: list[str]) -> User:
        user = await self._get_by_id(user_id)

        return await self.repository.add_relation(user, "WRITE_ACCESS", ou_ids)

    async def remove_read_access(self, user_id: str, ou_id: str) -> User:
        user = await self._get_by_id(user_id)

        if ou_id not in set(user.read):
            return user

        return await self.repository.remove_relation(user, "READ_ACCESS", [ou_id])

    async def remove_write_access(self, user_id: str, ou_id: str) -> User:
        user = await self._get_by_id(user_id)
        # TODO: check that relation is on list

        return await self.repository.remove_relation(user, "WRITE_ACCESS", [ou_id])
