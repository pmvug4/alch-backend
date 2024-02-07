import json

from loguru import logger

from core.config.telegram import telegram_settings
from core.telegram_notification.connection import SingletonAiohttpTelegram
from core.telegram_notification.models import TelegramMessage


async def send_telegram_message(msg: TelegramMessage, tlgrm_group: str = None, need_prefix: bool = True,
                                parse_mode: str = None) -> bool:
    if not telegram_settings.BOT_TOKEN or not tlgrm_group:
        logger.info(f"Telegram bot does not configured: set token and telegram group. {msg.format()}")
        return False

    if not telegram_settings.REPORTS_ENABLED:
        logger.info(f"Telegram message sent disabled: {msg.format()}")
        return False

    headers = {
        'Content-Type': 'application/json'
    }
    message = {
        'chat_id': tlgrm_group,
        'text': msg.format() if need_prefix else msg.msg
    }
    if parse_mode:
        message.update({'parse_mode': parse_mode})
    API_URL = 'https://api.telegram.org/bot%s/sendMessage' % telegram_settings.BOT_TOKEN

    client = SingletonAiohttpTelegram.get_aiohttp_client()
    resp = None
    text = ""
    try:
        async with client.post(API_URL,
                               data=json.dumps(message),
                               headers=headers
                               ) as resp:
            text = await resp.text()
            assert resp.status == 200

    except AssertionError as e:
        logger.exception(
            f"[TELEGRAM] (send_telegram_message) Unable to send message: {msg.format()} "
            f"cause: {resp.status}. text: {text}"
        )
        return False

    except Exception as e:
        logger.exception(f"[TELEGRAM] (send_telegram_message) Unable to send message: {msg.format()} cause: {repr(e)}")
        return False
    else:
        logger.debug(f"[TELEGRAM] (send_telegram_message) message sent")

    return True
