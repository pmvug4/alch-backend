import traceback
import loguru
import sys

from core.config.internal import logging_settings
from core.app_request import AppRequest


class Logger:
    def __init__(self):
        _format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | {extra[request_ip]} | "
            "{extra[request_id]} | <level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

        self._raw_logger: loguru.Logger = loguru.logger
        self._raw_logger.remove()
        self.load_extra()

        if logging_settings.LOG_FILE_LEVEL:
            self._raw_logger.add(
                "/app/logs/alch_back__{time:YYYY_MM_DD}.log",
                level=logging_settings.LOG_FILE_LEVEL.upper(),
                format=_format,
                rotation="00:00"
            )

        if logging_settings.LOG_STDOUT_LEVEL:
            self._raw_logger.add(
                sys.stdout,
                colorize=True,
                level=logging_settings.LOG_STDOUT_LEVEL.upper(),
                format=_format
            )

    def load_extra(self) -> None:
        self._raw_logger.configure(
            extra={
                "request_ip": AppRequest.ip.get(),
                "request_id": AppRequest.id,
                "api_name": AppRequest.api_name.get()
            }
        )

    def debug(self, msg):
        self._raw_logger.debug(msg)

    def info(self, msg):
        self._raw_logger.info(msg)

    def warning(self, msg):
        self._raw_logger.warning(msg)

    def error(self, msg):
        self._raw_logger.error(msg)

    def exception(self, msg):
        exc_text = traceback.format_exc()
        self._raw_logger.error(msg)
        self._raw_logger.error(exc_text)


log = Logger()
