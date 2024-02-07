from fastapi import Depends
from databases import Database

from core.notices.models import *
from core.notices import exceptions as notices_exceptions
from core.notices.depends import get_receiver
from core.notices import store as notices_store
from core.common.security import GetCurrentDB

from .exceptions import *


async def get_notification(
        notification_id: int,
        db: Database = Depends(GetCurrentDB()),
        receiver: NoticeReceiver = Depends(get_receiver)
) -> Notification:
    try:
        return await notices_store.Notification.get(
            db, pk=notification_id,
            assert_receiver_id=receiver.id
        )
    except notices_exceptions.NotificationAccessDenied:
        raise NotificationAccessDenied()
    except notices_exceptions.NotificationDoesNotExist:
        raise NotificationDoesNotExist()


async def get_notification_list(
        db: Database = Depends(GetCurrentDB()),
        page_size: int = 20,
        page_number: int = 1,
        from_time: datetime.datetime = None,
        to_time: datetime.datetime = None,
        viewed: Optional[bool] = None,
        receiver: NoticeReceiver = Depends(get_receiver),
) -> NotificationList:
    return await notices_store.Notification.get_list(
        db, receiver_id=receiver.id,
        page_number=page_number,
        page_size=page_size,
        after=from_time,
        before=to_time,
        viewed=viewed
    )
