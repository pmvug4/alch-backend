from pydantic import BaseSettings


class SmtpSettings(BaseSettings):
    HOSTNAME: str = 'smtp.gmail.com'
    PORT: int = 587

    LOGIN: str = 'plusover493@gmail.com'
    PASSWORD: str = 'faawsephphjrcpyb'

    class Config:
        env_prefix = 'SMTP_'


smtp_settings = SmtpSettings()
