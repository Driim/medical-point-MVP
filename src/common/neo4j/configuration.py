from pydantic import BaseSettings


class Neo4JConfiguration(BaseSettings):
    uri: str
    user: str
    password: str

    class Config:
        env_prefix = "neo4j_"
