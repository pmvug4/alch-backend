from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SmtpSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    HOSTNAME: str = Field('smtp.gmail.com', validation_alias='SMTP_HOSTNAME')
    PORT: int = Field(587, validation_alias='SMTP_PORT')
    LOGIN: str = Field(..., validation_alias='SMTP_LOGIN')
    PASSWORD: str = Field(..., validation_alias='SMTP_PASSWORD')


smtp_settings = SmtpSettings()
