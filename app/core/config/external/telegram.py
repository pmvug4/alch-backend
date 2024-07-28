from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TelegramSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    GLOBAL_PREFIX: str = Field('', validation_alias='TELEGRAM_GLOBAL_PREFIX')

    BOT_TOKEN: str = Field(..., validation_alias='TELEGRAM_BOT_TOKEN')
    ALARM_GROUP_ID: str = Field(..., validation_alias='TELEGRAM_ALARM_GROUP_ID')
    AUTH_GROUP_ID: str = Field(..., validation_alias='TELEGRAM_AUTH_GROUP_ID')

    SIZE_POOL_AIOHTTP: int = 10


telegram_settings = TelegramSettings()
