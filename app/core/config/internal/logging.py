from pydantic import BaseSettings, Field
from typing import Optional


class LoggingSettings(BaseSettings):
    LOG_PATH: Optional[str] = Field(None, env='LOG_PATH')
    LOG_FILE_LEVEL: Optional[str] = Field('INFO', env='LOG_FILE_LEVEL')
    LOG_STDOUT_LEVEL: Optional[str] = Field('DEBUG', env='LOG_STDOUT_LEVEL')
