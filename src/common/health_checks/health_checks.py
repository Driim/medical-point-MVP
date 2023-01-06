import logging

from fastapi import FastAPI
from fastapi_health import health

logger = logging.getLogger(__name__)


def register_health_checks(application: FastAPI, health_checks: list) -> None:
    if len(health_checks):
        logger.debug(f"Registering {len(health_checks)} health checks")
        application.add_api_route(
            "/_readiness",
            health(health_checks),
            tags=["__system__"],
        )
