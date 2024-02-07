from enum import Enum

from databases import Database
from pydantic import constr
from pytz import timezone

from api.preferences.store import Preferences, get_or_create_preferences_list
from api.users.store import get_user_ids_list_by_newsletter, get_all_users_ids, get_user, get_courier_user_ids, \
    get_customer_user_ids
from core.common import strings
from core.common.groups_and_roles import GROUP_COURIER, GROUP_CUSTOMER
from core.config.telegram import telegram_settings
from core.couriers.models.agreement_info import Agreement
from core.couriers.models.courier import Courier
from core.couriers.store import get_couriers_users_ids, get_car_info, get_person_info
from core.customers.store import get_employee
from core.customers.store.customers import get_customers_users_ids, get_customer, Customer
from core.notices import store
from core.notices.exceptions import BulkNotificationReceiverIdsDontMatchUserGroup
from core.notices.models import NotificationType, NoticeReceiver, NewsForm, News, NotificationMulticastForm, \
    BulkNotificationDBForm, BulkNotification
from core.orders.models import Order, OrderCourierView, RoutePoint, Route
from core.orders.store.route_points import get_route_point
from core.otp_provider import send_otp_msg
from core.push.services import send_pushes, PushMessage
from core.telegram_notification.models import TelegramMessage
from core.telegram_notification.task import send_telegram_message
from core.verification_request.models import VerificationRequest


async def send_notifications(
        db: Database,
        notification_type: NotificationType,
        title: constr(max_length=255),
        subtitle: constr(max_length=511) = None,
        description: constr(max_length=2047) = None,
        related_news_id: int = None,
        related_bulk_notification_id: int = None,

        # targets
        users_ids: list[int] = None,
        employees_ids: list[int] = None,
        couriers_ids: list[int] = None,

        force_with_push: bool = None,
        extra_push_data: dict[str, str] = None,
        check_newsletter: bool = True,
        enable_telegram_logging: bool = telegram_settings.PUSH_REPORTS_ENABLED
) -> None:
    users_data = await _get_receivers_and_preferences(
        db, users_ids=users_ids,
        employees_ids=employees_ids,
        couriers_ids=couriers_ids
    )

    if check_newsletter and notification_type is NotificationType.news:
        for user_id in list(users_data.keys()):
            if not users_data[user_id][1].news_enabled:
                users_data.pop(user_id)

    notifications = await store.Notification.create_multicast(
        db, form=NotificationMulticastForm(
            receivers_ids=[x[0].id for x in users_data.values()],
            news_id=related_news_id,
            bulk_notification_id=related_bulk_notification_id,
            type=notification_type,
            title=title,
            subtitle=subtitle,
            description=description
        )
    )
    # if not notifications:
    #     raise Exception(f"Wrong related_news_id ='{related_news_id}' ")
    # todo optimize
    for notification in notifications:
        for user_id in users_data.keys():
            if notification.receiver_id == users_data[user_id][0].id:
                users_data[user_id] = [*users_data[user_id], notification]
                continue

    if force_with_push is False:
        return

    if force_with_push is None:
        for user_id in list(users_data.keys()):
            if not users_data[user_id][1].push_enabled:
                users_data.pop(user_id)
    if enable_telegram_logging:
        tg_batch = 10
        messages = [
            f"""Success push
user_id : {receiver.user_id}
title : {title}
message : {chr(10).join([x for x in (subtitle, description) if x is not None])}
data : {(extra_push_data or {}) | {'notification_id': str(notification.id)} }"""
            for user_id, (receiver, _, notification) in users_data.items()
        ]
        for x in range(0, len(messages), tg_batch):
            chunk = messages[x: tg_batch + x]
            await send_telegram_message(TelegramMessage('\n\n'.join(chunk)),
                                        tlgrm_group=telegram_settings.ALARM_GROUP_ID)
    await send_pushes(
        [
            (
                PushMessage(
                    title=title,
                    message='\n'.join([x for x in (subtitle, description) if x is not None]),
                    data=(extra_push_data or {}) | {'notification_id': str(notification.id)}
                ),
                receiver
            )
            for user_id, (receiver, _, notification) in users_data.items()
        ]
    )


async def public_news(
        db: Database,
        title: constr(max_length=255),
        subtitle: constr(max_length=511) = None,
        description: constr(max_length=2047) = None,
        critical: bool = False
) -> News:
    news = await store.News.create(
        db, form=NewsForm(
            title=title,
            subtitle=subtitle,
            description=description
        )
    )

    users_ids: list[int]
    if critical:
        users_ids = await get_all_users_ids(db)
    else:
        users_ids = await get_user_ids_list_by_newsletter(db, enabled=True)

    await send_notifications(
        db, users_ids=users_ids,
        notification_type=NotificationType.news,
        title=news.title,
        subtitle=news.subtitle[:100] + '...' if len(news.subtitle) > 100 else news.subtitle,
        description=None,
        related_news_id=news.id,
        force_with_push=True if critical else None,
        check_newsletter=False if critical else True
    )

    return news


async def public_bulk_notification(
        db: Database,
        form: BulkNotificationDBForm,
) -> BulkNotification:
    if form.receiver_group_id == GROUP_COURIER:
        available_receiver_ids = await get_courier_user_ids(db)
    elif form.receiver_group_id == GROUP_CUSTOMER:
        available_receiver_ids = await get_customer_user_ids(db)
    else:
        raise RuntimeError

    if form.to_all:
        form.receiver_ids = available_receiver_ids
    elif wrong_user_ids := set(form.receiver_ids).difference(available_receiver_ids):
        raise BulkNotificationReceiverIdsDontMatchUserGroup(error_payload={"wrong_user_ids": list(wrong_user_ids)})

    bulk_notification = await store.BulkNotification.create(db, form)

    await send_notifications(
        db, users_ids=bulk_notification.receiver_ids,
        notification_type=NotificationType.bulk,
        title=bulk_notification.title,
        subtitle=bulk_notification.subtitle,
        description=bulk_notification.description,
        related_bulk_notification_id=bulk_notification.id,
    )

    return bulk_notification


class PushBackgroundAction:
    class Courier(str, Enum):
        reload_orders = 'reload_orders'
        reload_profile = 'reload_profile'

    class Customer(str, Enum):
        reload_orders = 'reload_orders'


class PushClickAction:
    class Courier(str, Enum):
        open_order_card = 'open_order_card'
        open_find_order_tab = 'open_find_order_tab'

    class Customer(str, Enum):
        open_order_card = 'open_order_card'
        open_add_order_tab = 'open_add_order_tab'


class SendCustomerNotification:
    class Push:
        class Delivery:
            @classmethod
            async def _send(
                    cls,
                    db: Database,
                    order: Order | OrderCourierView,
                    title: str,
                    subtitle: str = None,
                    description: str = None,
                    push_click_action: PushClickAction.Customer = None,
                    push_background_action: PushBackgroundAction.Customer = None,
                    extra_data: dict = None
            ) -> None:
                extra_data = extra_data or {}

                if push_background_action:
                    extra_data['push_background_action'] = f"{push_background_action}"

                return await send_notifications(
                    db, employees_ids=[order.employee_id],
                    notification_type=NotificationType.delivery,
                    title=title,
                    subtitle=subtitle,
                    description=description,
                    extra_push_data={
                                        'order_id': str(order.id),
                                        'order_title': str(order.title) if order.title else '',
                                        'order_status': f"{order.status}",
                                        'push_click_action': f"{push_click_action}"
                                    } | extra_data
                )

            @classmethod
            async def contract_rejected(
                    cls,
                    db: Database,
                    order: Order | OrderCourierView
            ) -> None:
                return await cls._send(
                    db,
                    order=order,
                    push_background_action=PushBackgroundAction.Customer.reload_orders,
                    **strings.CustomerNotifications.contract_rejected.format(order_id=order.id)
                )

            @classmethod
            async def courier_assigned(
                    cls,
                    db: Database,
                    order: Order | OrderCourierView
            ) -> None:
                return await cls._send(
                    db,
                    order=order,
                    push_background_action=PushBackgroundAction.Customer.reload_orders,
                    push_click_action=PushClickAction.Customer.open_order_card,
                    **strings.CustomerNotifications.courier_assigned.format(order_id=order.id),
                    extra_data={"order_assigned_to": f"{order.assigned_to or order.courier_id}"}
                )

            @classmethod
            async def courier_arrived(
                    cls,
                    db: Database,
                    order: Order | OrderCourierView
            ) -> None:
                return await cls._send(
                    db,
                    order=order,
                    push_background_action=PushBackgroundAction.Customer.reload_orders,
                    push_click_action=PushClickAction.Customer.open_order_card,
                    **strings.CustomerNotifications.courier_arrived.format(order_id=order.id)
                )

            @classmethod
            async def in_delivery(
                    cls,
                    db: Database,
                    order: Order | OrderCourierView
            ) -> None:
                return await cls._send(
                    db,
                    order=order,
                    push_background_action=PushBackgroundAction.Customer.reload_orders,
                    push_click_action=PushClickAction.Customer.open_order_card,
                    **strings.CustomerNotifications.in_delivery.format(order_id=order.id)
                )

            @classmethod
            async def delivered(
                    cls,
                    db: Database,
                    order: Order | OrderCourierView
            ) -> None:
                return await cls._send(
                    db,
                    order=order,
                    push_background_action=PushBackgroundAction.Customer.reload_orders,
                    push_click_action=PushClickAction.Customer.open_add_order_tab,
                    **strings.CustomerNotifications.delivered.format(order_id=order.id)
                )

            @classmethod
            async def published(
                    cls,
                    db: Database,
                    order: Order | OrderCourierView
            ) -> None:
                return await cls._send(
                    db,
                    order=order,
                    push_background_action=PushBackgroundAction.Customer.reload_orders,
                    push_click_action=PushClickAction.Customer.open_order_card,
                    **strings.CustomerNotifications.published.format(order_id=order.id)
                )

            @classmethod
            async def route_achieved(
                    cls,
                    db: Database,
                    order: Order | OrderCourierView,
                    route_point: RoutePoint
            ) -> None:
                return await cls._send(
                    db,
                    order=order,
                    push_background_action=PushBackgroundAction.Customer.reload_orders,
                    push_click_action=PushClickAction.Customer.open_order_card,
                    **strings.CustomerNotifications.route_achieved.format(recipient=route_point.name.capitalize(),
                                                                          address=route_point.address)
                )

            @classmethod
            async def courier_dropped(
                    cls,
                    db: Database,
                    order: Order | OrderCourierView
            ) -> None:
                return await cls._send(
                    db,
                    order=order,
                    push_background_action=PushBackgroundAction.Customer.reload_orders,
                    push_click_action=PushClickAction.Customer.open_order_card,
                    **strings.CustomerNotifications.courier_dropped.format(order_id=order.id)
                )

            @classmethod
            async def overdue(
                    cls,
                    db: Database,
                    order: Order | OrderCourierView
            ) -> None:
                return await cls._send(
                    db,
                    order=order,
                    push_background_action=PushBackgroundAction.Customer.reload_orders,
                    push_click_action=PushClickAction.Customer.open_order_card,
                    **strings.CustomerNotifications.overdue.format(order_id=order.id)
                )

    class SMS:
        # todo Переделать. Из-за test_user идет двойной запрос в базу. Done?
        # todo речь вообще не об этом была
        class Delivery:
            @classmethod
            async def _send(cls, db: Database, msg: str, customer: Customer):
                await send_otp_msg(
                    phone=(await get_user(db, pk=customer.user_id)).username,
                    msg=msg
                )

            @classmethod
            async def accepted(cls, db: Database, order: Order | OrderCourierView):
                if not (await get_employee(db, pk=order.employee_id)).test_user:
                    customer = await get_customer(db, employee_id=order.employee_id)
                    await cls._send(
                        db=db,
                        customer=customer,
                        **strings.CustomerSMS.accepted.format(title=order.title,
                                                              name=customer.name.capitalize())
                    )

            @classmethod
            async def delivered(cls, db: Database, order: Order | OrderCourierView):
                if not (await get_employee(db, pk=order.employee_id)).test_user:
                    customer = await get_customer(db, employee_id=order.employee_id)
                    await cls._send(
                        db=db,
                        customer=customer,
                        **strings.CustomerSMS.delivered.format(title=order.title,
                                                               name=customer.name.capitalize())
                    )

            @classmethod
            async def overdue(cls, db: Database, order: Order | OrderCourierView):
                if not (await get_employee(db, pk=order.employee_id)).test_user:
                    customer = await get_customer(db, employee_id=order.employee_id)
                    await cls._send(
                        db=db,
                        customer=customer,
                        **strings.CustomerSMS.overdue.format(order_id=order.id)
                    )

            class OtherPerson:
                @classmethod
                async def _send(cls, phone: str, msg: str):
                    await send_otp_msg(
                        phone=phone,
                        msg=msg
                    )

                @classmethod
                async def accepted(cls, db: Database, order: Order | OrderCourierView, route: Route):
                    car_info = await get_car_info(db, courier_id=order.courier_id)
                    person_info = await get_person_info(db, courier_id=order.courier_id)
                    departure_point = await get_route_point(db, pk=route.departure_point)
                    if not (await get_employee(db, pk=order.employee_id)).test_user:
                        await cls._send(
                            phone=departure_point.phone,
                            **strings.CustomerSMS.OtherPerson.accepted.format(
                                date="ASAP" if route.asap else f"{route.departure_time.low.astimezone(timezone('America/Los_Angeles')).strftime('%m/%d %I:%M %p')} - {route.departure_time.high.astimezone(timezone('America/Los_Angeles')).strftime('%I:%M %p')} LA",
                                address=f"{departure_point.address}, {departure_point.second_line}" if departure_point.second_line else departure_point.address,
                                fullname=person_info.fullname,
                                car_name=f"{car_info.base.mark} {car_info.base.model} {car_info.color} {car_info.number}",
                                phone=person_info.phone
                            )
                        )


class SendCourierNotification:
    class Push:
        class Delivery:
            @classmethod
            async def _send(
                    cls,
                    db: Database,
                    order: Order | OrderCourierView,
                    title: str,
                    subtitle: str = None,
                    description: str = None,
                    push_click_action: PushClickAction.Courier = None,
                    push_background_action: PushBackgroundAction.Courier = None,
                    extra_data: dict = None
            ) -> None:
                extra_data = extra_data or {}
                if push_background_action:
                    extra_data['push_background_action'] = f"{push_background_action}"

                return await send_notifications(
                    db, couriers_ids=[order.courier_id or order.assigned_to],
                    notification_type=NotificationType.delivery,
                    title=title,
                    subtitle=subtitle,
                    description=description,
                    extra_push_data={
                                        'order_id': str(order.id),
                                        'order_title': str(order.title or ''),
                                        'order_status': f"{order.status}",
                                        'push_click_action': f"{push_click_action}"
                                    } | extra_data
                )

            @classmethod
            async def verification_code(
                    cls,
                    db: Database,
                    order: Order | OrderCourierView,
                    password: str
            ) -> None:
                return await cls._send(
                    db,
                    order=order,
                    **strings.CourierNotifications.verification_code.format(
                        order_id=order.id,
                        password=password
                    ),
                    extra_data={
                        'order_verification_code': str(password)
                    }
                )

            @classmethod
            async def courier_assigned(
                    cls,
                    db: Database,
                    order: Order | OrderCourierView
            ) -> None:
                return await cls._send(
                    db,
                    order=order,
                    push_click_action=PushClickAction.Courier.open_order_card,
                    push_background_action=PushBackgroundAction.Courier.reload_orders,
                    **strings.CourierNotifications.courier_assigned.format(order_id=order.id),
                    extra_data={"order_assigned_to": f"{order.assigned_to or order.courier_id}"}
                )

            @classmethod
            async def courier_arrived(
                    cls,
                    db: Database,
                    order: Order | OrderCourierView
            ) -> None:
                return await cls._send(
                    db,
                    order=order,
                    push_click_action=PushClickAction.Courier.open_order_card,
                    push_background_action=PushBackgroundAction.Courier.reload_orders,
                    **strings.CourierNotifications.courier_arrived.format(order_id=order.id)
                )

            @classmethod
            async def in_delivery(
                    cls,
                    db: Database,
                    order: Order | OrderCourierView
            ) -> None:
                return await cls._send(
                    db,
                    order=order,
                    push_click_action=PushClickAction.Courier.open_order_card,
                    push_background_action=PushBackgroundAction.Courier.reload_orders,
                    **strings.CourierNotifications.in_delivery.format(order_id=order.id)
                )

            @classmethod
            async def delivered(
                    cls,
                    db: Database,
                    order: Order | OrderCourierView
            ) -> None:
                return await cls._send(
                    db,
                    order=order,
                    push_click_action=PushClickAction.Courier.open_find_order_tab,
                    push_background_action=PushBackgroundAction.Courier.reload_orders,
                    **strings.CourierNotifications.delivered.format(order_id=order.id)
                )

            @classmethod
            async def new_contract(
                    cls,
                    db: Database,
                    order: Order | OrderCourierView
            ) -> None:
                return await cls._send(
                    db,
                    order=order,
                    push_click_action=PushClickAction.Courier.open_order_card,
                    push_background_action=PushBackgroundAction.Courier.reload_orders,
                    **strings.CourierNotifications.new_contract.format()
                )

            @classmethod
            async def canceled_by_customer(
                    cls,
                    db: Database,
                    order: Order | OrderCourierView
            ) -> None:
                return await cls._send(
                    db,
                    order=order,
                    push_click_action=PushClickAction.Courier.open_find_order_tab,
                    push_background_action=PushBackgroundAction.Courier.reload_orders,
                    **strings.CourierNotifications.canceled_by_customer.format(order_id=order.id)
                )

            @classmethod
            async def confirmed(
                    cls,
                    db: Database,
                    order: Order | OrderCourierView
            ) -> None:
                return await cls._send(
                    db,
                    order=order,
                    push_click_action=PushClickAction.Courier.open_find_order_tab,
                    push_background_action=PushBackgroundAction.Courier.reload_orders,
                    **strings.CourierNotifications.confirmed.format(order_id=order.id)
                )

            @classmethod
            async def canceled_by_cooperator(
                    cls,
                    db: Database,
                    order: Order | OrderCourierView
            ) -> None:
                return await cls._send(
                    db,
                    order=order,
                    push_click_action=PushClickAction.Courier.open_find_order_tab,
                    push_background_action=PushBackgroundAction.Courier.reload_orders,
                    **strings.CourierNotifications.canceled_by_cooperator.format(order_id=order.id)
                )

            @classmethod
            async def canceled_by_courier(
                    cls,
                    db: Database,
                    order: Order | OrderCourierView
            ) -> None:
                return await cls._send(
                    db,
                    order=order,
                    push_click_action=PushClickAction.Courier.open_find_order_tab,
                    push_background_action=PushBackgroundAction.Courier.reload_orders,
                    **strings.CourierNotifications.canceled_by_courier.format(order_id=order.id)
                )

        class Verification:
            @classmethod
            async def _send(
                    cls,
                    db: Database,
                    request: VerificationRequest,
                    title: str,
                    subtitle: str = None,
                    description: str = None,
                    push_background_action: PushBackgroundAction.Courier = None
            ) -> None:
                extra_data = {}

                if push_background_action:
                    extra_data['push_background_action'] = f"{push_background_action}"

                return await send_notifications(
                    db, couriers_ids=[request.courier_id],
                    notification_type=NotificationType.account,
                    title=title,
                    subtitle=subtitle,
                    description=description,
                    extra_push_data={
                                        'verification_request_id': str(request.id),
                                        'verification_request_status': f"{request.status}"
                                    } | extra_data
                )

            @classmethod
            async def approve(
                    cls,
                    db: Database,
                    request: VerificationRequest
            ) -> None:
                return await cls._send(
                    db,
                    request=request,
                    push_background_action=PushBackgroundAction.Courier.reload_profile,
                    **strings.CourierNotifications.courier_verification_approved.format()
                )

            @classmethod
            async def decline(
                    cls,
                    db: Database,
                    request: VerificationRequest
            ) -> None:
                return await cls._send(
                    db,
                    request=request,
                    push_background_action=PushBackgroundAction.Courier.reload_profile,
                    **strings.CourierNotifications.courier_verification_declined.format(
                        request_description=str(request.message)
                    )
                )

        class Agreement:
            @classmethod
            async def _send(
                    cls,
                    db: Database,
                    agreement: Agreement,
                    courier: Courier,
                    title: str,
                    subtitle: str = None,
                    description: str = None,
                    push_background_action: PushBackgroundAction.Courier = None
            ) -> None:
                extra_data = {}

                if push_background_action:
                    extra_data['push_background_action'] = f"{push_background_action}"

                return await send_notifications(
                    db, couriers_ids=[courier.id],
                    notification_type=NotificationType.account,
                    title=title,
                    subtitle=subtitle,
                    description=description,
                    extra_push_data={
                                        'agreement_id': str(agreement.id),
                                    } | extra_data
                )

            @classmethod
            async def consent_docs_is_ready(
                    cls,
                    db: Database,
                    agreement: Agreement,
                    courier: Courier,
            ) -> None:
                return await cls._send(
                    db,
                    agreement=agreement,
                    courier=courier,
                    push_background_action=PushBackgroundAction.Courier.reload_profile,
                    **strings.CourierNotifications.courier_consent_docs_is_ready.format()
                )

        class Referral:
            @classmethod
            async def _send(
                    cls,
                    db: Database,
                    courier_id: int,
                    title: str,
                    subtitle: str = None,
                    description: str = None,
                    push_click_action: PushClickAction.Courier = None,
                    push_background_action: PushBackgroundAction.Courier = None,
                    extra_data: dict = None
            ) -> None:
                extra_data = extra_data or {}
                if push_background_action:
                    extra_data['push_background_action'] = f"{push_background_action}"

                return await send_notifications(
                    db, couriers_ids=[courier_id],
                    notification_type=NotificationType.delivery,
                    title=title,
                    subtitle=subtitle,
                    description=description,
                    extra_push_data={
                                        'push_click_action': f"{push_click_action}"
                                    } | extra_data
                )

            @classmethod
            async def sender_courier(
                    cls,
                    db: Database,
                    courier_id: int
            ) -> None:
                return await cls._send(
                    db,
                    courier_id=courier_id,
                    push_click_action=PushClickAction.Courier.open_order_card,
                    push_background_action=PushBackgroundAction.Courier.reload_orders,
                    **strings.CourierNotifications.sender_courier.format()
                )

            @classmethod
            async def recipient_courier(
                    cls,
                    db: Database,
                    courier_id: int
            ) -> None:
                return await cls._send(
                    db,
                    courier_id=courier_id,
                    push_click_action=PushClickAction.Courier.open_order_card,
                    push_background_action=PushBackgroundAction.Courier.reload_orders,
                    **strings.CourierNotifications.recipient_courier.format()
                )


async def _get_receivers_and_preferences(
        db: Database,
        users_ids: list[int] = None,
        employees_ids: list[int] = None,
        couriers_ids: list[int] = None
) -> dict[int, (NoticeReceiver, Preferences)]:
    users_ids = users_ids or []
    users_ids += await get_customers_users_ids(db, employees_ids=employees_ids)
    users_ids += await get_couriers_users_ids(db, couriers_ids=couriers_ids)
    users_ids = list(set(users_ids))

    receivers_pairs = await store.NoticeReceiver.get_or_create_list(db, users_ids=users_ids)
    preferences_pairs = await get_or_create_preferences_list(db, users_ids=users_ids)

    if len(receivers_pairs) != len(preferences_pairs):
        raise RuntimeError

    return {
        user_id: (receiver, preferences_pairs[user_id])
        for user_id, receiver in receivers_pairs.items()
    }
