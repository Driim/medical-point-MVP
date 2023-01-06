from fastapi import Depends

from src.structures.dal.users_repository import UsersRepository
from src.structures.domain.users.exceptions import UserNotFound
from src.structures.domain.users.models import User, UserCreateDto


class UserService:
    repository: UsersRepository

    def __init__(
        self,
        repository: UsersRepository = Depends(UsersRepository),
    ) -> None:
        self.repository = repository

    async def _get_by_id(self, id: str) -> User:
        user = await self.repository.get_by_id(id)

        if not user:
            raise UserNotFound(id)

        return user

    async def get_user_by_id(self, user_id: str) -> User:
        return await self._get_by_id(user_id)

    async def have_read_access(self, user_id: str, organization_id: str) -> bool:
        # TODO: implement
        return True

    async def have_write_access(self, user_id: str, organization_id: str) -> bool:
        # TODO: implement
        return True

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

        # TODO: check that relation is on list

        return await self.repository.remove_relation(user, "READ_ACCESS", [ou_id])

    async def remove_write_access(self, user_id: str, ou_id: str) -> User:
        user = await self._get_by_id(user_id)
        # TODO: check that relation is on list

        return await self.repository.remove_relation(user, "WRITE_ACCESS", [ou_id])
