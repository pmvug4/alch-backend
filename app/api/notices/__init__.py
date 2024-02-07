from databases import Database
from fastapi import APIRouter, Depends

from api.notices.depends import get_notification as check_notification

from core.common.security import GetCurrentDB, get_current_user, User
import core.notices.store as notice_store
from core.exception import IncorrectCredentials, AppZoneIsExpired
from core.notices import exceptions as notices_exceptions
from core.notices.depends import get_receiver
from core.notices.models import *
from core.schemas import get_response_models, prepare_response_scheme, BaseOK
from core.app_zone import AppZoneStore

from . import depends
from .exceptions import *
from .models import *


router = APIRouter(tags=["notices"])

_base_exc = [
    IncorrectCredentials
]


@router.get(
    "/receiver",
    description="Returns self receiver info.",
    response_model=NoticeReceiver,
    responses=get_response_models(
        "get_self_receiver",
        exceptions=[
            *_base_exc
        ],
        with_422_error=False,
        resp200ok=prepare_response_scheme(NoticeReceiver)
    )
)
async def get_self_notice_receiver(
        receiver: NoticeReceiver = Depends(get_receiver)
):
    return receiver


@router.post(
    "/receiver",
    description="Save token and platform",
    response_model=NoticeReceiver,
    responses=get_response_models(
        "create_receiver",
        exceptions=[
            *_base_exc
        ],
        with_422_error=False,
        resp200ok=prepare_response_scheme(NoticeReceiver)
    )
)
async def post_notice_receiver(
        data: NoticeReceiverUpdate,
        db: Database = Depends(GetCurrentDB()),
        receiver: NoticeReceiver = Depends(get_receiver),
        user: User = Depends(get_current_user)
):
    app_zone = await AppZoneStore.db_get(db, name=user.app_zone)
    if app_zone.expired:
        raise AppZoneIsExpired

    _receiver = await notice_store.NoticeReceiver.update_notice_receiver(
        db, receiver.id,
        data.app_token,
        data.platform
    )
    return _receiver


@router.get(
    "/notification/list",
    description="Get notification list.",
    response_model=NotificationList,
    responses=get_response_models(
        "get_notification_list",
        exceptions=_base_exc,
        with_422_error=False,
        resp200ok=prepare_response_scheme(NotificationList)
    )
)
async def get_notification_list(
        notifications: NotificationList = Depends(depends.get_notification_list)
):
    return notifications


@router.get(
    "/notification/{notification_id}",
    description="Get notification.",
    response_model=Notification,
    responses=get_response_models(
        "get_notification",
        exceptions=[
            *_base_exc,
            NotificationAccessDenied,
            NotificationDoesNotExist
        ],
        with_422_error=False,
        resp200ok=prepare_response_scheme(Notification)
    )
)
async def get_notification(
        notification: Notification = Depends(depends.get_notification)
):
    return notification


@router.patch(
    "/notification/{notification_id}/viewed",
    description="Mark notification as viewed.",
    response_model=Notification,
    responses=get_response_models(
        "mark_notification_viewed",
        exceptions=[
            *_base_exc,
            NotificationAccessDenied,
            NotificationDoesNotExist
        ],
        with_422_error=False,
        resp200ok=prepare_response_scheme(Notification)
    )
)
async def mark_notification_viewed(
        viewed: bool,
        db: Database = Depends(GetCurrentDB()),
        notification: Notification = Depends(depends.get_notification)
):
    return await notice_store.Notification.mark_viewed(
        db, pk=notification.id,
        viewed=viewed
    )


@router.patch(
    "/notification/viewed",
    description="Mark notification list as viewed.",
    response_model=BaseOK,
    responses=get_response_models(
        "mark_notification_list_viewed",
        exceptions=[
            *_base_exc,
            NotificationAccessDenied,
            NotificationDoesNotExist
        ],
        with_422_error=False,
        resp200ok=prepare_response_scheme(BaseOK)
    )
)
async def mark_notification_list_viewed(
        viewed: bool,
        notification_list: list[int],
        db: Database = Depends(GetCurrentDB()),
        receiver: NoticeReceiver = Depends(get_receiver)
):
    try:
        await notice_store.Notification.check_list_access(db, notification_list, receiver.id)
    except notices_exceptions.NotificationAccessDenied:
        raise NotificationAccessDenied()
    except notices_exceptions.NotificationDoesNotExist:
        raise NotificationDoesNotExist()
    await notice_store.Notification.mark_viewed_list(db, notification_list, viewed)
    return BaseOK()
