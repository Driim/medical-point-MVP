import logging
from uuid import uuid4

from aioarango.database import StandardDatabase
from fastapi import Depends

from src.common.arango.middleware import get_session
from src.structures.dal.neo4j.utils import transform_to_dict
from src.structures.domain.users.models import User, UserCreateDto

logger = logging.getLogger(__name__)


class ArangoUsersRepository:
    OU_COLLECTION = "organizations_units"
    USERS_COLLECTION = "users"
    READ_GRAPH = "read_access_graph"
    READ_EDGE = "read_access"
    WRITE_GRAPH = "read_access_graph"
    WRITE_EDGE = "write_access"

    def __init__(self, database: StandardDatabase = Depends(get_session)):
        self.database = database

    async def get_by_id(self, user_id: str) -> User:
        write_graph = self.database.graph(self.WRITE_GRAPH)
        read_graph = self.database.graph(self.READ_GRAPH)

        users = write_graph.vertex_collection(self.USERS_COLLECTION)
        user = await users.get(user_id)
        logger.info(user)

        if not user:
            return None

        write_edges = await write_graph.edges(self.WRITE_EDGE, user['_id'], direction='out')
        write = [edge['_to'].split("/")[1] for edge in write_edges.get('edges')]
        logger.info(write)

        read_edges = await read_graph.edges(self.READ_EDGE, user['_id'], direction='out')
        read = [edge['_to'].split("/")[1] for edge in read_edges.get('edges')]
        logger.info(read)

        return User(
            id=user['_key'],
            name=user['name'],
            write=write,
            read=read,
        )

    async def delete(self, user: User) -> None:
        write_graph = self.database.graph(self.WRITE_GRAPH)
        users = write_graph.vertex_collection(self.USERS_COLLECTION)

        await users.delete(user.id)

    async def create(self, dto: UserCreateDto) -> User:
        params = transform_to_dict(dto)

        read_access = params["read"]
        del params["read"]

        write_access = params["write"]
        del params["write"]

        params["_key"] = str(uuid4())

        write_graph = self.database.graph(self.WRITE_GRAPH)
        users_collection = write_graph.vertex_collection(self.USERS_COLLECTION)
        metadata = await users_collection.insert(params)

        if read_access:
            read_graph = self.database.graph(self.READ_GRAPH)
            edges = read_graph.edge_collection(self.READ_EDGE)
            read_edges = []
            for ou_id in read_access:
                read_edges.append({
                    '_from': metadata['_id'],
                    '_to': self.OU_COLLECTION + "/" + ou_id
                })

            logger.info("Read access edges:")
            logger.info(read_edges)

            await edges.import_bulk(read_edges)

        if write_access:
            edges = write_graph.edge_collection(self.WRITE_EDGE)
            write_edges = []
            for ou_id in write_access:
                write_edges.append({
                    '_from': metadata['_id'],
                    '_to': self.OU_COLLECTION + "/" + ou_id
                })

            await edges.import_bulk(write_edges)

        return User(
            id=metadata['_key'],
            name=params['name'],
            read=read_access,
            write=write_access
        )

    async def add_relation(self, user: User, relation: str, ou_ids: list[str]) -> User:
        pass

    async def remove_relation(
            self,
            user: User,
            relation: str,
            ou_ids: list[str],
    ) -> User:
        pass

    async def has_access_right(
            self,
            user_id: str,
            organization_id: str,
            root_ou: str,
            access_right: str,
    ) -> bool:
        cursor_ou = await self.database.aql.execute(
            """
            FOR e IN OUTBOUND 
            SHORTEST_PATH @start 
            TO @end child_of 
            RETURN e._key
            """,
            bind_vars={
                'start': "organizations_units/" + organization_id,
                'end': "organizations_units/" + root_ou,
            }
        )

        ou_path = [doc async for doc in cursor_ou]

        cursor_user = await self.database.aql.execute(
            """
            FOR e IN OUTBOUND @user @access
            RETURN e._key
            """,
            bind_vars={
                'user': "users/" + user_id,
                'access': access_right.lower(),
            }
        )

        orgs = [doc async for doc in cursor_user]
        intersection = set(ou_path).intersection(orgs)
        return True if len(intersection) else False

    async def have_write_access_by_outlet(
            self,
            user_id: str,
            outlet_id: str,
            root_ou: str,
            access_right: str,
    ) -> bool:
        graph = self.database.graph("outlets_graph")
        collection = graph.vertex_collection("outlets")
        outlet = await collection.get(outlet_id)

        return await self.has_access_right(
            user_id,
            outlet.get('organization_unit_id'),
            root_ou,
            access_right
        )
