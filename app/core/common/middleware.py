import json
import time
import uuid

from fastapi import Request
from loguru import logger
from starlette.responses import Response

from core.config.common import RunStates, common_settings
from core.config.gcs import gcs_settings
from core.context import request_id_context, request_ip_context, endpoint_name_context
from .alarm import time_alarm_handler


async def request_middleware(request: Request, call_next):
    # BEFORE REQUEST ---------------------------------------------------------------------------------------------------

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

    extra = {"request_id": request_id, "ip": request_ip}
    logger.configure(extra=extra)
    try:
        response = await call_next(request)
    except Exception as e:
        # set request_id for exceptions handlers
        e.__setattr__("_request-id-for-response", request_id)
        raise e

    # AFTER REQUEST ----------------------------------------------------------------------------------------------------
    process_time = round((time.monotonic() - start_time) * 1000)

    if common_settings.RUN_STATE in (RunStates.LOCAL, RunStates.DEBUG, RunStates.PP):
        response.headers["X-Process-Time"] = f"{process_time}ms"
        logger.debug(f"{endpoint_name} X-Process-Time:  {process_time}ms")

    await time_alarm_handler(request, process_time, request_id)

    if not gcs_settings.USE_GCS and endpoint_name.startswith("static"):
        return response

    if response.status_code == 200 and endpoint_name not in ["docs", "openapi.json"]:
        # оборачиваем ответ
        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        try:
            resp = json.loads(body)
            resp = json.dumps({"error": None,
                               "data": resp
                               }).encode()
        except Exception as e:
            logger.error(f"unable_to_envelope_response: {repr(e)}")

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

    response.headers["X-Request-ID"] = request_id

    return response
