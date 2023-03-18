from pydantic import BaseSettings

from src.common.arango import ArangConfiguration
from src.common.logger.configuration import LoggerConfiguration
from src.common.neo4j.configuration import Neo4JConfiguration


class Configuration(BaseSettings):
    logging: LoggerConfiguration = LoggerConfiguration()
    neo4j: Neo4JConfiguration = Neo4JConfiguration()
    root_ou: str
    uptrace_dsn: str
    arango: ArangConfiguration = ArangConfiguration()
