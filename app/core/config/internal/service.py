from pydantic import BaseSettings, Field
from typing import Optional


class ServiceSettings(BaseSettings):
    SERVICE_NAME: str = Field('alch-backend', env='SERVICE_NAME')
    API_KEY: str = Field(..., env='SERVICE_API_KEY')
    TESTING_KEY: Optional[str] = Field(None, env='SERVICE_TESTING_KEY')
    SHOW_API_DOCS: bool = Field(True, env='SERVICE_SHOW_API_DOCS')


service_settings = ServiceSettings()
