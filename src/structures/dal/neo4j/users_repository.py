import logging

from fastapi import Depends
from neo4j import AsyncSession, AsyncTransaction

from src.common.neo4j import get_session, get_transaction
from src.structures.dal.neo4j.utils import transform_to_dict
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

    async def get_by_id(self, user_id: str) -> User:
        query = """
            MATCH (u:USER {id: $id})
            WHERE u.deleted IS NULL
            OPTIONAL MATCH (u)-[:READ_ACCESS]->(r_ou:OrganizationUnit|RootOrganizationUnit)
            OPTIONAL MATCH (u)-[:WRITE_ACCESS]->(w_ou:OrganizationUnit|RootOrganizationUnit)
            WITH u, w_ou, collect(r_ou.id) as read_ou
            WITH u, read_ou, collect(w_ou.id) as write_ou
            RETURN u {.*, read: read_ou, write: write_ou} as user
            """

        result = await (await self.tx.run(query, id=user_id)).single()
        return User(**result["user"]) if result is not None else None

    async def delete(self, user: User) -> None:
        query = "MATCH (u:USER { id: $id }) SET u.deleted = true"

        # TODO: do we need to remove all existing relation?

        await (await self.tx.run(query, id=user.id)).single()

    async def create(self, dto: UserCreateDto) -> User:
        query = ""
        params = transform_to_dict(dto)

        if "read" in params:
            query += "MATCH (r_ou:OrganizationUnit|RootOrganizationUnit) WHERE r_ou.id in $read "

        if "write" in params:
            query += "MATCH (w_ou:OrganizationUnit|RootOrganizationUnit) WHERE w_ou.id in $write "

        query += "CREATE (u:USER { id: randomUUID(), name: $name }) "

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
        logger.warning(result["user"])

        return User(**result["user"]) if result is not None else None

    async def add_relation(self, user: User, relation: str, ou_ids: list[str]) -> User:
        query = "MATCH (u:USER {id: $id}) "
        query += (
            "MATCH (ou:OrganizationUnit|RootOrganizationUnit) WHERE ou.id in $ou_ids "
        )
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
        query = (
            "MATCH (ou:OrganizationUnit|RootOrganizationUnit) WHERE ou.id in $ou_ids "
        )
        # TODO: refactor
        if relation == "READ_ACCESS":
            query += "MATCH (u:USER {id: $id})-[r:READ_ACCESS]->(ou)"
        else:
            query += "MATCH (u:USER {id: $id})-[r:WRITE_ACCESS]->(ou)"

        query += "DELETE r"

        await (await self.tx.run(query, id=user.id, ou_ids=ou_ids)).single()

        return await self.get_by_id(user.id)

    async def has_access_right(
        self,
        user_id: str,
        organization_id: str,
        root_ou: str,
        access_right: str,
    ) -> bool:
        query = "OPTIONAL MATCH (o:OrganizationUnit {id: $organization_unit})"
        query += "-[:CHILD_OF*0..10]->(p:OrganizationUnit)-[:CHILD_OF*0..10]->(root:RootOrganizationUnit)"
        query += " WITH collect(p.id) + [$root_ou] as path_ids"
        query += " MATCH (u:USER {id: $id})"
        query += f"-[r:{access_right}]->"
        query += "(ou:OrganizationUnit|RootOrganizationUnit)"
        query += " WHERE ou.id IN path_ids AND u.deleted IS NULL RETURN r"

        result = await (
            await self.tx.run(
                query,
                id=user_id,
                organization_unit=organization_id,
                root_ou=root_ou,
            )  # noqa
        ).single()
        return True if result is not None else False

    async def have_write_access_by_outlet(
        self,
        user_id: str,
        outlet_id: str,
        root_ou: str,
        access_right: str,
    ) -> bool:
        query = "OPTIONAL MATCH (o:Outlet {id: $outlet_id})-[:BELONG_TO]->(:OrganizationUnit)"
        query += "-[:CHILD_OF*0..10]->(p:OrganizationUnit)-[:CHILD_OF*0..10]->(root:RootOrganizationUnit)"
        query += " WITH collect(p.id) + [$root_ou] as path_ids"
        query += " MATCH (u:USER {id: $id})"
        query += f"-[r:{access_right}]->"
        query += "(ou:OrganizationUnit|RootOrganizationUnit)"
        query += " WHERE ou.id IN path_ids AND u.deleted IS NULL RETURN r"

        result = await (
            await self.tx.run(
                query,
                id=user_id,
                outlet_id=outlet_id,
                root_ou=root_ou,
            )  # noqa
        ).single()
        return True if result is not None else False
