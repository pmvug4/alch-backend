from pydantic import BaseSettings, SecretStr


class RedisSettings(BaseSettings):
    HOST: str = None
    PASSWORD: SecretStr = ""
    PORT: str = "6379"
    class Config:
        env_prefix = 'REDIS_'


redis_settings = RedisSettings()

