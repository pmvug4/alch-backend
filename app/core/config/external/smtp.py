from pydantic import BaseSettings, Field


class SmtpSettings(BaseSettings):
    HOSTNAME: str = Field('smtp.gmail.com', env='SMTP_HOSTNAME')
    PORT: int = Field(587, env='SMTP_PORT')
    LOGIN: str = Field(..., env='SMTP_LOGIN')
    PASSWORD: str = Field(..., env='SMTP_PASSWORD')


smtp_settings = SmtpSettings()
