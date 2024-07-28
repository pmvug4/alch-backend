from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from typing import Optional


class ServiceSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    SERVICE_NAME: str = Field('alch-backend', validation_alias='SERVICE_NAME')
    API_KEY: str = Field(..., validation_alias='SERVICE_API_KEY')
    TESTING_KEY: Optional[str] = Field(None, validation_alias='SERVICE_TESTING_KEY')
    SHOW_API_DOCS: bool = Field(True, validation_alias='SERVICE_SHOW_API_DOCS')
    RETURN_FULL_VALIDATION_ERRORS: bool = Field(True, validation_alias='SERVICE_RETURN_FULL_VALIDATION_ERRORS')
    RETURN_PROCESS_TIME: bool = Field(True, validation_alias='SERVICE_RETURN_PROCESS_TIME')


service_settings = ServiceSettings()
