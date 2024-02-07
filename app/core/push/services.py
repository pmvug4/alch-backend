from starlette.concurrency import run_in_threadpool
import firebase_admin
from firebase_admin import messaging
from contextlib import suppress
from itertools import groupby

from core.config.common import common_settings

from core.notices.models import NoticeReceiver
from core.push.models import AppPlatform, PushMessage
import asyncio

from loguru import logger

firebase_courier_cred = firebase_admin.credentials.Certificate(
    common_settings.GOOGLE_APPLICATION_CREDENTIALS_COURIER
)
firebase_courier_app = firebase_admin.initialize_app(
    firebase_courier_cred,
    name="COURIER_APP"
)

firebase_customer_cred = firebase_admin.credentials.Certificate(
    common_settings.GOOGLE_APPLICATION_CREDENTIALS_CUSTOMER
)

firebase_customer_app = firebase_admin.initialize_app(
    firebase_customer_cred,
    name="CUSTOMER_APP"
)


def _send_fcm_messages(messages: list[messaging.Message]):
    with suppress(Exception):
        messaging.send_all(messages, app=firebase_courier_app)

    with suppress(Exception):
        messaging.send_all(messages, app=firebase_customer_app)


_app_handlers = {
    AppPlatform.android: _send_fcm_messages,
    AppPlatform.ios: _send_fcm_messages,
    AppPlatform.web: _send_fcm_messages,
    # AppPlatform.huawei: send_huawei_message
}


def _filter_data(data: list[(PushMessage, NoticeReceiver)]) -> list[(PushMessage, NoticeReceiver)]:
    resp = []
    incomplete = []
    for obj in data:
        receiver: NoticeReceiver = obj[1]
        if receiver and receiver.platform and receiver.app_token:
            resp.append(obj)
        else:
            incomplete.append(obj)

    logger.debug(f"Filtered users with wrong FCM data {incomplete}")
    return resp


async def send_pushes(data: list[(PushMessage, NoticeReceiver)]) -> None:
    logger.debug(f"Call send_push: {data}")

    data = _filter_data(data)

    for platform, data_by_platform in groupby(data, lambda x: x[1].platform):
        asyncio.get_event_loop().create_task(  # noqa
            run_in_threadpool(
                _app_handlers[platform],
                messages=[message.prepare_message(receiver) for message, receiver in data_by_platform]
            ))
