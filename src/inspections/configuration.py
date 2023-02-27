from pydantic import BaseSettings

from src.common.clickhouse.configuration import ClickhouseConfiguration
from src.common.logger.configuration import LoggerConfiguration


class Configuration(BaseSettings):
    logging: LoggerConfiguration = LoggerConfiguration()
    clickhouse: ClickhouseConfiguration = ClickhouseConfiguration()
    structures_url: str
