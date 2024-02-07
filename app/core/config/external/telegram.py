from typing import Optional

from pydantic import BaseSettings, Field

from core.config.common import common_settings


class TelegramSettings(BaseSettings):
    BOT_TOKEN: str = Field(..., env='TELEGRAM_BOT_TOKEN')
    ALARM_GROUP_ID: str = Field(..., env='TELEGRAM_ALARM_GROUP_ID')
    AUTH_GROUP_ID: str = Field(..., env='TELEGRAM_AUTH_GROUP_ID')

    SIZE_POOL_AIOHTTP: int = 10


telegram_settings = TelegramSettings()
