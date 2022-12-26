import logging

from fastapi import APIRouter, FastAPI
from src.common.neo4j import Transactional, TransactionalRouter

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Organizations"], route_class=TransactionalRouter)


@router.get("/{id}")
async def read_item(id: str):
    logger.info(f"Reading {id}")
    return "Hello World!"


@Transactional()
@router.put("/{id}")
async def put_item(id: str):
    logger.info(f"Reading {id} {put_item.__transactional__}")
    return "Put Hello World!"


def register_organizations_router(application: FastAPI, version: str) -> None:
    logger.debug("Registering market campaign router")
    router.tags.append(version)
    application.include_router(router, prefix=version + "/organizations")
