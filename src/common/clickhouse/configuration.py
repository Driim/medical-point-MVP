from pydantic import BaseSettings


class ClickhouseConfiguration(BaseSettings):
    url: str
    echo: bool = False

    class Config:
        env_prefix = "clickhouse_"
