from pydantic import BaseSettings, Field


class DBSettings(BaseSettings):
    DB_TYPE: str = "postgresql"
    DB_CONNECTOR: str = "asyncpg"

    HOST: str = Field(..., env="POSTGRES_HOST")
    PORT: int = Field(..., env="POSTGRES_PORT")
    USER: str = Field(..., env="POSTGRES_USER")
    PASSWORD: str = Field(..., env="POSTGRES_PASSWORD")

    DB: str = Field(..., env="POSTGRES_DB")
    MIN_CONNECTIONS: int = Field(..., env="POSTGRES_MIN_CONNECTIONS")
    MAX_CONNECTIONS: int = Field(..., env="POSTGRES_MAX_CONNECTIONS")

    @property
    def database_url(self):
        return f"{self.DB_TYPE}+{self.DB_CONNECTOR}://" \
               f"{self.USER}:{self.PASSWORD}@" \
               f"{self.HOST}:{self.PORT}/" \
               f"{self.DB}"


db_settings = DBSettings()
