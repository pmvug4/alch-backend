from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    DB_TYPE: str = "postgresql"
    DB_CONNECTOR: str = "asyncpg"

    HOST: str = Field(..., validation_alias="POSTGRES_HOST")
    PORT: int = Field(..., validation_alias="POSTGRES_PORT")
    USER: str = Field(..., validation_alias="POSTGRES_USER")
    PASSWORD: str = Field(..., validation_alias="POSTGRES_PASSWORD")

    DB: str = Field(..., validation_alias="POSTGRES_DB")
    MIN_CONNECTIONS: int = Field(..., validation_alias="POSTGRES_MIN_CONNECTIONS")
    MAX_CONNECTIONS: int = Field(..., validation_alias="POSTGRES_MAX_CONNECTIONS")

    @property
    def database_url(self):
        return f"{self.DB_TYPE}+{self.DB_CONNECTOR}://" \
               f"{self.USER}:{self.PASSWORD}@" \
               f"{self.HOST}:{self.PORT}/" \
               f"{self.DB}"


db_settings = DBSettings()
