from pydantic import BaseSettings


class ArangConfiguration(BaseSettings):
    uri: str
    user: str
    password: str
    db: str

    class Config:
        env_prefix = "arango_"