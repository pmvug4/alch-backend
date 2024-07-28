import aiosmtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from core.config.smtp import smtp_settings
from core.config.telegram import telegram_settings
from core.smtp.exceptions import UnexpectedSmtpExtension

from loguru import logger

from core.telegram.models import TelegramErrorMessage
from core.telegram.task import send_telegram_message


async def create_message(title: str, text: str, receiver_email: str) -> str:
    message = MIMEMultipart()
    message["To"] = receiver_email
    message["Subject"] = title
    message.attach(MIMEText(text, "plain"))
    return message.as_string()


async def _send_mail(message: str, receiver_email: str) -> bool:
    try:
        smtp = aiosmtplib.SMTP(hostname=smtp_settings.HOSTNAME, port=smtp_settings.PORT)
        await smtp.connect()
        await smtp.login(username=smtp_settings.LOGIN, password=smtp_settings.PASSWORD)
        await smtp.sendmail(sender=smtp_settings.LOGIN, recipients=receiver_email, message=message)
        await smtp.quit()
    except Exception as exc:
        logger.error(exc)
        await send_telegram_message(TelegramErrorMessage(
            f"Failed to send mail. \nMessage: {message} \nReceiver_email: {receiver_email} \nError: {exc}"),
            telegram_settings.ALARM_GROUP_ID)
    return True


async def send_mail(title: str, text: str, receiver_email: str) -> bool:
    return await _send_mail(message=await create_message(title, text, receiver_email), receiver_email=receiver_email)
