from pydantic import BaseSettings

from src.common.clickhouse.configuration import ClickhouseConfiguration
from src.common.kafka import KafkaConfiguration
from src.common.logger.configuration import LoggerConfiguration


class Configuration(BaseSettings):
    logging: LoggerConfiguration = LoggerConfiguration()
    clickhouse: ClickhouseConfiguration = ClickhouseConfiguration()
    kafka: KafkaConfiguration = KafkaConfiguration()
    structures_url: str
