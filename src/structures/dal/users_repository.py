import logging

from fastapi import Depends
from neo4j import AsyncSession, AsyncTransaction

from src.common.neo4j import get_session, get_transaction
from src.structures.dal.utils import transform_to_dict
from src.structures.domain.users.models import User, UserCreateDto

logger = logging.getLogger(__name__)


class UsersRepository:
    def __init__(
        self,
        session: AsyncSession = Depends(get_session),
        transaction: AsyncTransaction | None = Depends(get_transaction),
    ) -> None:
        self.session = session
        self.transaction = transaction
        self.tx = transaction if transaction else session

    async def get_by_id(self, id: str) -> User:
        query = """
            MATCH (u:USER {id: $id})
            WHERE u.deleted IS NULL
            OPTIONAL MATCH (u)-[:READ_ACCESS]->(r_ou:ORGANIZATION_UNIT|ROOT_ORGANIZATION_UNIT)
            OPTIONAL MATCH (u)-[:WRITE_ACCESS]->(w_ou:ORGANIZATION_UNIT|ROOT_ORGANIZATION_UNIT)
            WITH u, w_ou, collect(r_ou.id) as read_ou
            WITH u, read_ou, collect(w_ou.id) as write_ou
            RETURN u {.*, read: read_ou, write: write_ou} as user
            """

        result = await (await self.tx.run(query, id=id)).single()

        logger.warn(result)

        return User(**result["user"]) if result is not None else None

    async def delete(self, user: User) -> None:
        query = "MATCH (u:USER { id: $id }) SET u.deleted = true"

        # TODO: do we need to remove all existing relation?

        await (await self.tx.run(query, id=user.id)).single()

    async def create(self, dto: UserCreateDto) -> User:
        query = ""
        params = transform_to_dict(dto)

        if "read" in params:
            query += "MATCH (r_ou:ORGANIZATION_UNIT|ROOT_ORGANIZATION_UNIT) WHERE r_ou.id in $read "

        if "write" in params:
            query += "MATCH (w_ou:ORGANIZATION_UNIT|ROOT_ORGANIZATION_UNIT) WHERE w_ou.id in $write "

        query += "CREATE (u:USER { id: randomUUID() }) "

        if "read" in params:
            query += "CREATE (u)-[:READ_ACCESS]->(r_ou) "

        if "write" in params:
            query += "CREATE (u)-[:WRITE_ACCESS]->(w_ou) "

        query += " RETURN u {"
        result_lines = [".*"]
        if "read" in params:
            result_lines.append("read: [r_ou.id]")

        if "write" in params:
            result_lines.append("write: [w_ou.id]")

        query += ", ".join(result_lines)

        query += "} as user"

        logger.debug(query)
        result = await (await self.tx.run(query, **params)).single()
        logger.warn(result["user"])

        return User(**result["user"]) if result is not None else None

    async def add_relation(self, user: User, relation: str, ou_ids: list[str]) -> User:
        query = "MATCH (u:USER {id: $id}) "
        query += "MATCH (ou:ORGANIZATION_UNIT|ROOT_ORGANIZATION_UNIT) WHERE ou.id in $ou_ids "
        query += f"CREATE (u)-[r:{relation}]->(ou)"

        logger.debug(query)
        await (await self.tx.run(query, id=user.id, ou_ids=ou_ids)).single()

        return await self.get_by_id(user.id)

    async def remove_relation(
        self,
        user: User,
        relation: str,
        ou_ids: list[str],
    ) -> User:
        query = "MATCH (ou:ORGANIZATION_UNIT|ROOT_ORGANIZATION_UNIT) WHERE ou.id in $ou_ids "
        # TODO: refactor
        if relation == "READ_ACCESS":
            query += "MATCH (u:USER {id: $id})-[r:READ_ACCESS]->(ou)"
        else:
            query += "MATCH (u:USER {id: $id})-[r:WRITE_ACCESS]->(ou)"

        query += "DELETE r"

        logger.debug(query)
        await (await self.tx.run(query, id=user.id, ou_ids=ou_ids)).single()

        return await self.get_by_id(user.id)
