import re

from fastapi import Request

from core.config.common import common_settings
from core.otp_provider import send_response_time_alarm

API_TIME_ALARM_MAPPING = {
    r"/api/v1/customer/order/invoice/list": 15000,
    r"/api/v1/customer/order/(?P<order_id>[^/]+)/photo": None,
    r"/api/v1/customer/order/(?P<order_id>[^/]+)/publish": common_settings.TIME_BEFORE_TG_ALARM * 2,
    r"/api/v1/courier/registration/driver_info/photo": None,
    r"/api/v1/courier/registration/car_info/photo": None,
    r"/api/v1/courier/profile/driver_info/photo": None,
    r"/api/v1/courier/profile/car_info/photo": None,
    r"/api/v1/courier/order/delivery/(?P<order_id>[^/]+)/point/(?P<point_id>[^/]+)/photo": None,
    r"/api/v1/courier/profile/me/avatar": None,
    r"/api/v1/webhooks/stripe/": common_settings.TIME_BEFORE_TG_ALARM + 5000,
    r".*": common_settings.TIME_BEFORE_TG_ALARM
}


async def time_alarm_handler(
        request: Request,
        process_time: int,
        request_id: str
) -> None:
    for pattern, admissible_process_time in API_TIME_ALARM_MAPPING.items():
        if re.match(pattern, request.url.path):
            if admissible_process_time and process_time >= admissible_process_time:
                await send_response_time_alarm(request, process_time, request_id)

            return
