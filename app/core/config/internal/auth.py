from pydantic import BaseSettings, Field


class AuthSettings(BaseSettings):
    AUTH_ALG: str = 'HS256'
    AUTH_SECRET: str = Field(..., env='AUTH_SECRET')
    AUTH_PASSWORD_SALT: str = Field(..., env='AUTH_PASSWORD_SALT')

    AUTH_BY_COOKIE: bool = True

    AUTH_ACCESS_TOKEN_EXPIRES_IN_SECONDS: int = Field(3600, env='AUTH_ACCESS_TOKEN_EXPIRES_IN_SECONDS')

    AUTH_OTP_PASSWORD_VALID_PERIOD_SECONDS: int = Field(180, env='AUTH_OTP_PASSWORD_VALID_PERIOD_SECONDS')
    AUTH_OTP_PASSWORD_CHECKS: int = Field(3, env='AUTH_OTP_PASSWORD_CHECKS')
    AUTH_OTP_RETRY_PERIOD_SECONDS: int = Field(300, env='AUTH_OTP_RETRY_PERIOD_SECONDS')
    AUTH_OTP_PASSWORD_LENGTH: int = 6


auth_settings = AuthSettings()
