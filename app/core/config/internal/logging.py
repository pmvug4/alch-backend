from pydantic import BaseSettings, Field
from typing import Optional


class LoggingSettings(BaseSettings):
    LOG_FILE_LEVEL: Optional[str] = Field('INFO', env='LOG_FILE_LEVEL')
    LOG_STDOUT_LEVEL: Optional[str] = Field('DEBUG', env='LOG_STDOUT_LEVEL')


logging_settings = LoggingSettings()
