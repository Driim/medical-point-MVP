import logging

from fastapi import APIRouter, Depends, FastAPI
from fastapi_restful.cbv import cbv

from src.common.neo4j import Transactional, TransactionalRouter
from src.structures.domain.users import UserService
from src.structures.domain.users.models import (
    User,
    UserAddReadAccessDto,
    UserAddWriteAccessDto,
    UserCreateDto,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Users"], route_class=TransactionalRouter)


@cbv(router)
class UsersController:
    service: UserService = Depends(UserService)

    @router.get("/users/{user_id}", response_model=User)
    async def get_user_by_id(self, user_id: str):
        return await self.service.get_user_by_id(user_id)

    @Transactional()
    @router.post("/users", response_model=User)
    async def create_user(self, dto: UserCreateDto):
        return await self.service.create(dto)

    @Transactional()
    @router.delete("/users/{user_id}")
    async def delete_user(self, user_id: str):
        return await self.service.delete(user_id)

    @Transactional()
    @router.put("/users/{user_id}/read", response_model=User)
    async def add_read_access(self, user_id: str, dto: UserAddReadAccessDto):
        return await self.service.add_read_access(user_id, dto.read)

    @Transactional()
    @router.put("/users/{user_id}/write", response_model=User)
    async def add_write_access(self, user_id: str, dto: UserAddWriteAccessDto):
        return await self.service.add_write_access(user_id, dto.write)

    @Transactional()
    @router.delete("/users/{user_id}/read/{ou_id}")
    async def delete_read_access(self, user_id: str, ou_id: str):
        return await self.service.remove_read_access(user_id, ou_id)

    @Transactional()
    @router.delete("/users/{user_id}/write/{ou_id}")
    async def delete_write_access(self, user_id: str, ou_id: str):
        return await self.service.remove_write_access(user_id, ou_id)


def register_users_router(application: FastAPI, version: str) -> None:
    logger.debug("Registering users controller")
    router.tags.append(version)
    application.include_router(router, prefix=version)
