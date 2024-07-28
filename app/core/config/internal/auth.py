from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    AUTH_ALG: str = 'HS256'
    AUTH_SECRET: str = Field(..., validation_alias='AUTH_SECRET')
    AUTH_PASSWORD_SALT: str = Field(..., validation_alias='AUTH_PASSWORD_SALT')

    AUTH_BY_COOKIE: bool = True

    AUTH_ACCESS_TOKEN_EXPIRES_IN_SECONDS: int = Field(3600, validation_alias='AUTH_ACCESS_TOKEN_EXPIRES_IN_SECONDS')

    AUTH_OTP_PASSWORD_VALID_PERIOD_SECONDS: int = Field(180, validation_alias='AUTH_OTP_PASSWORD_VALID_PERIOD_SECONDS')
    AUTH_OTP_PASSWORD_CHECKS: int = Field(3, validation_alias='AUTH_OTP_PASSWORD_CHECKS')
    AUTH_OTP_RETRY_PERIOD_SECONDS: int = Field(300, validation_alias='AUTH_OTP_RETRY_PERIOD_SECONDS')
    AUTH_OTP_PASSWORD_LENGTH: int = 6
    AUTH_CACHE_SESSION_ALIVE_SECONDS: int = 300


auth_settings = AuthSettings()
