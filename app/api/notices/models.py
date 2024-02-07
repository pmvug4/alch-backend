from typing import Optional

from pydantic import BaseModel

from core.notices.models import News, Notification
from core.push.models import AppPlatform


class NoticeConsumingResponse(BaseModel):
    news: list[News]
    notifications: list[Notification]


class NoticeReceiverUpdate(BaseModel):
    platform: Optional[AppPlatform]
    app_token: Optional[str]
