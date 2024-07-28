from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from typing import Optional


class LoggingSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    LOG_FILE_LEVEL: Optional[str] = Field('INFO', validation_alias='LOG_FILE_LEVEL')
    LOG_STDOUT_LEVEL: Optional[str] = Field('DEBUG', validation_alias='LOG_STDOUT_LEVEL')


logging_settings = LoggingSettings()
