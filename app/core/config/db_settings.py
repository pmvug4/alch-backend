from pydantic import BaseSettings, Field


class PLDBSettings(BaseSettings):
    DB_TYPE: str = "postgresql"
    DB_CONNECTOR: str = "asyncpg"

    HOST: str = Field(..., env="POSTGRES_HOST")
    PORT: int = Field(..., env="POSTGRES_PORT")
    USER: str = Field(..., env="POSTGRES_USER")
    PASSWORD: str = Field(..., env="POSTGRES_PASSWORD")

    DB: str = Field(..., env="POSTGRES_DB")
    MIN_CONNECTIONS: int = Field(..., env="MIN_CONNECTIONS")
    MAX_CONNECTIONS: int = Field(..., env="MAX_CONNECTIONS")

    DB_ALARM_THRESHOLD: float = Field(1, env="DB_ALARM_THRESHOLD")
    DB_LOG_EXEC_TIME: bool = Field(0, env="DB_LOG_EXEC_TIME")

    @property
    def DATABASE_URL(self):
        return f"{self.DB_TYPE}+{self.DB_CONNECTOR}://" \
               f"{self.USER}:{self.PASSWORD}@" \
               f"{self.HOST}:{self.PORT}/" \
               f"{self.DB}"


class PLDemoDBSettings(PLDBSettings):
    DB: str = Field(..., env="POSTGRES_DEMO_DB")
    MIN_CONNECTIONS: int = Field(..., env="DEMO_MIN_CONNECTIONS")
    MAX_CONNECTIONS: int = Field(..., env="DEMO_MAX_CONNECTIONS")


db_settings = PLDBSettings()
demo_db_settings = PLDemoDBSettings()
