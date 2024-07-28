from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    HOST: str = Field(..., validation_alias='REDIS_HOST')
    PASSWORD: SecretStr = Field(..., validation_alias='REDIS_PASSWORD')
    PORT: int = Field(6379, validation_alias='REDIS_PORT')


redis_settings = RedisSettings()
