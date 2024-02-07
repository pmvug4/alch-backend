from typing import Optional

from pydantic import BaseSettings

from core.config.common import common_settings


class TelegramSettings(BaseSettings):
    PREFIX: str = common_settings.RUN_STATE.name
    BOT_TOKEN: Optional[str] = None
    ALARM_GROUP_ID: Optional[str] = None
    REPORTS_ENABLED: str = True
    PUSH_REPORTS_ENABLED: bool = False
    SIZE_POOL_AIOHTTP: int = 10
    AUTH_GROUP_ID: str = None
    ORDER_GROUP_ID: Optional[str] = None

    class Config:
        env_prefix = 'TELEGRAM_'


telegram_settings = TelegramSettings()
