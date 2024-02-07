import sys
from ..context import request_ip_context, request_id_context
from loguru import logger

from core.config.common import common_settings


def configure_logging() -> None:
    """
    https://loguru.readthedocs.io/en/stable/api/logger.html
    """

    logging_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | {extra[ip]} | {extra[request_id]} | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>"
    logger.configure(extra={"ip": request_ip_context.get(), "request_id": request_id_context.get()})
    logger.remove()

    logger.add(
        "/app/logs/{time:YYYY_MM_DD}__" + common_settings.SERVICE_NAME + ".log",
        level=common_settings.LOG_FILE_LEVEL,
        format=logging_format,
        rotation="00:00"
    )

    if common_settings.LOG_STDOUT:
        logger.add(
            sys.stdout,
            colorize=True,
            level=common_settings.LOG_STDOUT_LEVEL,
            format=logging_format
        )

    if common_settings.LOG_SERIALIZE:
        logger.add(
            "/app/logs/{time:YYYY_MM_DD}__" + common_settings.SERVICE_NAME + "_serialize.log",
            level=common_settings.LOG_FILE_LEVEL,
            format=logging_format,
            serialize=True,
            rotation="00:00"
        )
