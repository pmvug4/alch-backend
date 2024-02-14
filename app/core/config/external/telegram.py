from pydantic import BaseSettings, Field


class TelegramSettings(BaseSettings):
    GLOBAL_PREFIX: str = Field('', env='TELEGRAM_GLOBAL_PREFIX')

    BOT_TOKEN: str = Field(..., env='TELEGRAM_BOT_TOKEN')
    ALARM_GROUP_ID: str = Field(..., env='TELEGRAM_ALARM_GROUP_ID')
    AUTH_GROUP_ID: str = Field(..., env='TELEGRAM_AUTH_GROUP_ID')

    SIZE_POOL_AIOHTTP: int = 10


telegram_settings = TelegramSettings()
