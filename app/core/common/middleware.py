import json
import time
import re

from fastapi import Request
from starlette.responses import Response

from core.config.internal import run_state_settings, service_settings
from core.telegram import tg_send_alarm
from core.app_request import AppRequest
from core.localization import Language
from core.logs import log


async def request_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)

    AppRequest.gen_id()
    AppRequest.ip.set(getattr(getattr(request, 'client', None), 'host', '127.0.0.1'))
    AppRequest.api_name.set(request.scope.get('path'))
    AppRequest.lang.set(request.headers.get('Content-Language', Language.en))

    log.load_extra()

    start_time = time.monotonic()

    response = await call_next(request)
    response.headers['X-Request-ID'] = AppRequest.id

    process_time = round((time.monotonic() - start_time) * 1000)

    if service_settings.RETURN_PROCESS_TIME:
        response.headers["X-Process-Time"] = f"{process_time}ms"

    await _time_alarm_handler(
        request=request,
        process_time=process_time,
        request_id=AppRequest.id  # noqa
    )

    if (
            response.status_code == 200
            and
            AppRequest.api_name.get().replace('/', '') not in ["docs", "openapi.json"]
    ):
        # оборачиваем ответ
        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        resp = json.loads(body)
        resp = json.dumps({"error": None, "data": resp}).encode()

        headers = dict(response.headers)
        headers.update({"content-length": str(len(resp))})

        log.debug(f"Response: [{request.method}] -> {request.url} <<< {resp} ")

        return Response(
            content=resp,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type
        )
    else:
        return response


_API_TIME_ALARM_MAPPING = {
    r".*": run_state_settings.TELEGRAM_SERVICE_ALARM_EXEC_THRESHOLD_MS
}


async def _time_alarm_handler(
        request: Request,
        process_time: int,
        request_id: str
) -> None:
    for pattern, admissible_process_time in _API_TIME_ALARM_MAPPING.items():
        if re.match(pattern, request.url.path):
            if admissible_process_time and process_time >= admissible_process_time:
                await tg_send_alarm(
                    f"{request_id} Long query {request.url.path} execution {process_time/100:.2d}s."
                )

            return
