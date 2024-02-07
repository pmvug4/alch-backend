from enum import Enum
from typing import Optional
from typing import TYPE_CHECKING
from pydantic import BaseModel, validator, root_validator

from firebase_admin import messaging
from firebase_admin.messaging import Notification


if TYPE_CHECKING:
    from core.notices.models import NoticeReceiver


class AppPlatform(str, Enum):
    android = "android"
    ios = "ios"
    huawei = "huawei"
    web = "web"


class PushType(str, Enum):
    silent = "silent"
    notification = "notification"


class PushMessage(BaseModel):
    message: Optional[str]
    title: Optional[str]
    data: dict
    type: PushType = PushType.notification

    @validator('data', pre=True)
    def _validate_data(cls, value: Optional[dict]) -> dict:
        return value or {}

    @root_validator(skip_on_failure=True)
    def _validate_message(cls, values: dict):
        if not values.get('title') and not values.get('message'):
            raise ValueError("To send notification push message provide title or message")
        return values

    def _prepare_notification(self) -> Notification:
        return Notification(title=self.title or "", body=self.message or "")

    def _prepare_android_notification_message(self, receiver: "NoticeReceiver") -> messaging.Message:
        message = messaging.Message(
            data=self.data or {},
            token=receiver.app_token,
            notification=self._prepare_notification(),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound='default'
                    ),
                ),
            )
        )
        return message

    def _prepare_android_silent_message(self, receiver: "NoticeReceiver") -> messaging.Message:
        message = messaging.Message(
            data=self.data or {},
            token=receiver.app_token,

        )
        return message

    def _prepare_web_message(self, receiver: "NoticeReceiver") -> messaging.Message:
        message = messaging.Message(
            data=self.data or {},
            token=receiver.app_token,
            notification=self._prepare_notification()
        )
        return message

    def _prepare_ios_notification_message(self, receiver: "NoticeReceiver") -> messaging.Message:
        message = messaging.Message(
            data=self.data or {},
            token=receiver.app_token,
            notification=self._prepare_notification(),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound='default'
                    ),
                ),
            )
        )
        return message

    def _prepare_ios_silent_message(self, receiver: "NoticeReceiver") -> messaging.Message:
        aps = messaging.Aps(content_available=True)
        payload = messaging.APNSPayload(aps)
        message = messaging.Message(
            data=self.data or {},
            token=receiver.app_token,
            apns=messaging.APNSConfig(payload=payload)
        )
        return message

    def prepare_message(self, receiver: "NoticeReceiver") -> messaging.Message:
        push_formatters = {
            AppPlatform.android: {
                PushType.notification: self._prepare_android_notification_message,
                PushType.silent: self._prepare_android_silent_message,
            },
            AppPlatform.ios: {
                PushType.notification: self._prepare_ios_notification_message,
                PushType.silent: self._prepare_ios_notification_message,
            },
            AppPlatform.web: {
                PushType.notification: self._prepare_web_message,
                PushType.silent: self._prepare_web_message,
            },
        }

        return push_formatters[receiver.platform][self.type](receiver)  # noqa
