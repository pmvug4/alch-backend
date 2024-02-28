import json
import time
import uuid
import re

from fastapi import Request
from loguru import logger
from starlette.responses import Response

from core.config.internal import run_state_settings, service_settings
from core.context import request_id_context, request_ip_context, endpoint_name_context
from core.telegram import tg_send_alarm


async def request_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)

    request_id = str(uuid.uuid4())
    start_time = time.monotonic()
    endpoint_name = request.scope.get('path').replace('/', '')

    try:
        request_ip = request.client.host
    except AttributeError:
        request_ip = '127.0.0.1'

    request_id_context.set(request_id)
    request_ip_context.set(request_ip)
    endpoint_name_context.set(endpoint_name)

    extra = {
        "request_id": request_id,
        "ip": request_ip
    }

    logger.configure(extra=extra)
    try:
        response = await call_next(request)
    except Exception as e:
        # set request_id for exceptions handlers
        e.__setattr__("_request-id-for-response", request_id)
        raise e

    # AFTER REQUEST ----------------------------------------------------------------------------------------------------
    process_time = round((time.monotonic() - start_time) * 1000)
    logger.debug(f"{endpoint_name} X-Process-Time:  {process_time}ms")

    if service_settings.RETURN_PROCESS_TIME:
        response.headers["X-Process-Time"] = f"{process_time}ms"

    await _time_alarm_handler(
        request=request,
        process_time=process_time,
        request_id=request_id
    )

    if endpoint_name.startswith("static"):
        return response
    elif response.status_code == 200 and endpoint_name not in ["docs", "openapi.json"]:
        # оборачиваем ответ
        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        try:
            resp = json.loads(body)
            resp = json.dumps({"error": None, "data": resp}).encode()
        except Exception as e:
            logger.error(f"unable_to_envelope_response: {repr(e)}")
            raise
        else:
            headers = dict(response.headers)
            headers.update({"content-length": str(len(resp))})
            logger.debug(f"({request_ip}) Response: [{request.method}] -> {request.url} >>> {resp} <<<")
            return Response(
                content=resp,
                status_code=response.status_code,
                headers=headers,
                media_type=response.media_type
            )
    else:
        response.headers["X-Request-ID"] = request_id
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
