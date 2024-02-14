from core.config.external import telegram_settings

from .task import send_telegram_message, TelegramMessage


async def tg_send_alarm(msg: str):
    return await send_telegram_message(
        msg=TelegramMessage(msg),
        tg_group=telegram_settings.ALARM_GROUP_ID,
        __wait=False
    )
