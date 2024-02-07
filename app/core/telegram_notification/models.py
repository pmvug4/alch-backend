from core.config.telegram import telegram_settings
from core.context import request_id_context


class TelegramMessage:
    def __init__(self, msg):
        self.msg = msg

    def format(self):
        return f"{telegram_settings.PREFIX}: {self.msg}"


class TelegramErrorMessage(TelegramMessage):
    def format(self):
        request_id = request_id_context.get()
        return f"{telegram_settings.PREFIX}: ({request_id}) {self.msg}"
