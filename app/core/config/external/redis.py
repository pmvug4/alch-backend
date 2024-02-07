from pydantic import BaseSettings, SecretStr, Field


class RedisSettings(BaseSettings):
    HOST: str = Field(..., env='REDIS_HOST')
    PASSWORD: SecretStr = Field(..., env='REDIS_PASSWORD')
    PORT: int = Field(6379, env='REDIS_PORT')


redis_settings = RedisSettings()
