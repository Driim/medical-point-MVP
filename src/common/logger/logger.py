import logging.config
from uvicorn.logging import DefaultFormatter
from typing import Callable
from src.common.logger.configuration import LogLevel, LogType, LoggerConfiguration


def mock_configuration_generator(level: LogLevel):
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {"level": level, "handlers": ["colored"]},
        "handlers": {
            "colored": {"class": "logging.StreamHandler", "formatter": "colored"},
        },
        "formatters": {
            "colored": {
                "()": DefaultFormatter,
                "fmt": "%(levelprefix)s - [%(name)s:%(lineno)d] %(message)s",
            },
        },
        "loggers": {
            "uvicorn.access": {
                "handlers": ["colored"],
                "propagate": False,
                "level": level,
            },
            "uvicorn.error": {
                "handlers": ["colored"],
                "propagate": False,
                "level": level,
            },
            "uvicorn": {"handlers": ["colored"], "propagate": False, "level": level},
        },
    }


def initialize_logger(config: LoggerConfiguration):
    logger_configuration_map: dict[LogType, Callable] = {
        "DEPLOY": mock_configuration_generator,
        "PLAIN": mock_configuration_generator,
    }

    configuration_generator = logger_configuration_map[config.type]
    configuration = configuration_generator(config.level)
    if configuration:
        logging.config.dictConfig(configuration)
