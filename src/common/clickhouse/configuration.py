from pydantic import BaseSettings


class ClickhouseConfiguration(BaseSettings):
    url: str
    echo: bool = False
    pool_size: int = 5

    class Config:
        env_prefix = "clickhouse_"
