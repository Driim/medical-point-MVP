from pydantic import BaseSettings

from src.common.logger.configuration import LoggerConfiguration


class Configuration(BaseSettings):
    logging: LoggerConfiguration = LoggerConfiguration()
    structures_url: str
