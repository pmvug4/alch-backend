from core.config.external.telegram import telegram_settings
from core.app_request import AppRequest


class TelegramMessage:
    def __init__(self, msg):
        self.msg = msg

    def format(self):
        return f"{telegram_settings.GLOBAL_PREFIX}{self.msg}"


class TelegramErrorMessage(TelegramMessage):
    def format(self):
        return f"{telegram_settings.GLOBAL_PREFIX}({AppRequest.id}) {self.msg}"
