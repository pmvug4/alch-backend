import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, constr, root_validator

from core.cooperators.models import Cooperator
from core.models import Pagination
from core.photos import Photo
from core.push.models import AppPlatform


class NotificationType(str, Enum):
    account = 'account'
    delivery = 'delivery'
    news = 'news'
    bulk = 'bulk'


class NewsForm(BaseModel):
    title: constr(max_length=255)
    subtitle: Optional[constr(max_length=511)] = None
    description: Optional[constr(max_length=2047)] = None


class News(NewsForm):
    id: int
    ctime: datetime.datetime


class NewsList(BaseModel):
    pagination: Pagination
    news: list[News]


class NoticeReceiverForm(BaseModel):
    user_id: int


class NoticeReceiver(NoticeReceiverForm):
    id: int
    app_token: Optional[str]
    platform: Optional[AppPlatform]


class _BaseNotificationForm(BaseModel):
    type: NotificationType
    news_id: Optional[int]
    bulk_notification_id: Optional[int]
    title: constr(max_length=255)
    subtitle: Optional[constr(max_length=511)] = None
    description: Optional[constr(max_length=2047)] = None


class NotificationForm(_BaseNotificationForm):
    receiver_id: int


class NotificationMulticastForm(_BaseNotificationForm):
    receivers_ids: list[int]


class Notification(NotificationForm):
    id: int
    viewed: bool
    ctime: datetime.datetime


class NotificationList(BaseModel):
    pagination: Pagination
    notifications: list[Notification]


class BulkNotificationForm(BaseModel):
    title: constr(max_length=255)
    subtitle: Optional[constr(max_length=511)]
    description: Optional[constr(max_length=2047)]
    receiver_ids: Optional[list[int]] = Field(None, description="User IDs of couriers or customers")
    to_all: bool

    @root_validator
    def check_receivers(cls, values):
        if not values.get("title") and not values.get("subtitle") and not values.get("description"):
            raise ValueError("Either title, subtitle or description must be specified!")
        if not values.get("receiver_ids") and not values.get("to_all"):
            raise ValueError("Either receiver_ids must be specified or to_all is set to true!")
        return values


class BulkNotificationDBForm(BulkNotificationForm):
    cooperator_id: int
    receiver_group_id: int


class BulkNotificationReceiver(BaseModel):
    user_id: int
    name: Optional[str]
    surname: Optional[str]
    middle_name: Optional[str]
    avatar: Optional[Photo]


class BulkNotification(BulkNotificationDBForm):
    id: int
    ctime: datetime.datetime
    cooperator: Cooperator
    receivers: Optional[list[BulkNotificationReceiver]]


class BulkNotificationList(BaseModel):
    pagination: Pagination
    bulk_notifications: list[BulkNotification]
