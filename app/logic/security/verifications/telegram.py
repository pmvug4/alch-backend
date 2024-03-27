from pydantic import EmailStr

from core.telegram import TelegramMessage, send_telegram_message
from core.config.external import telegram_settings


async def send_email_code(
        email: EmailStr,
        code: str
):
    await send_telegram_message(
        msg=TelegramMessage(f"Email: {email} verification code is {code}"),
        tg_group=telegram_settings.AUTH_GROUP_ID,
    )

    # todo переключатель: оптравлять код на почту или в телеграм
