import asyncio
import json
from typing import Optional

import aiohttp
from loguru import logger

from core.background.controller import BackgroundTasks

from core.config.external.telegram import telegram_settings
from core.telegram.connection import SingletonAiohttpTelegram
from core.telegram.models import TelegramMessage


async def send_telegram_message(
        msg: TelegramMessage,
        tg_group: str,
        parse_mode: str = None,
        __wait: bool = False
) -> Optional[bool]:
    if not telegram_settings.BOT_TOKEN:
        logger.error(f"Telegram bot does not configured: set token and telegram group. {msg.format()}")
        return False

    async def _send():
        headers = {
            'Content-Type': 'application/json'
        }

        data = {
            'chat_id': tg_group,
            'text': msg.format()
        }

        if parse_mode:
            data['parse_mode'] = parse_mode

        url = 'https://api.telegram.org/bot%s/sendMessage' % telegram_settings.BOT_TOKEN
        client = SingletonAiohttpTelegram.get_aiohttp_client()

        for i in range(5):
            try:
                async with client.post(
                        url,
                        data=json.dumps(data),
                        headers=headers
                ) as resp:
                    if resp.status == 200:
                        return True
                    elif resp.status != 200:
                        text = await resp.text()
                        logger.exception(
                            f"[TELEGRAM] (send_telegram_message) Unable to send message: {msg.format()} "
                            f"cause: {resp.status}. text: {text}. Retry {i}"
                        )
            except aiohttp.ClientConnectionError:
                logger.exception(
                    f"[TELEGRAM] (send_telegram_message) Unable to send message: "
                    f"connection error. Retry {i}"
                )

            await asyncio.sleep(i)

        return False

    if __wait:
        return await _send()
    else:
        await BackgroundTasks.create(_send())
