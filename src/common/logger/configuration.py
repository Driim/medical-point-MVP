from typing import Literal
from pydantic import BaseSettings

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]
LogType = Literal["DEPLOY", "PLAIN"]


class LoggerConfiguration(BaseSettings):
    level: LogLevel = "DEBUG"
    type: LogType = "PLAIN"

    class Config:
        env_prefix = "log_"  # LOG_LEVEL, LOG_TYPE
