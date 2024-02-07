from typing import Union

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_422_UNPROCESSABLE_ENTITY

from core.common import strings
from core.config.common import common_settings
from core.exception import AppHTTPException

from core.otp_provider import send_internal_exception_alarm

from loguru import logger


async def http422_error_handler(
        request: Request,
        exc: Union[RequestValidationError, ValidationError],
) -> JSONResponse:
    exception_info = f"Response: [{request.method}] -> {request.url} >>> {request.headers} <<<"
    logger.exception(f"{exception_info}\nException: {repr(exc)}\n Body: {exc.body}")

    return JSONResponse(
        content={
            "error": {
                "error_msg": strings.validation_error,
                "error_name": "parsedataerror",
                "error_payload":
                    {
                        "validation_errors": exc.errors() if common_settings.HTTP_EXTRA_INFO else ""
                    }
            },

            "data": None
        },
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
    )


async def http_error_handler(request: Request, exc: AppHTTPException) -> JSONResponse:
    exception_info = f"Response: [{request.method}] -> {request.url} "
    logger.info(f"{exception_info} Exception: {repr(exc)}")
    logger.debug(f"{request.headers}")

    return JSONResponse(
        content={
            "error": {
                "error_msg": exc.detail,
                "error_name": exc.error_name,
                "error_payload": exc.error_payload
            },
            "data": None
        },
        status_code=exc.status_code)


async def http_unhadlederror_handler(_: Request, exc: HTTPException) -> JSONResponse:
    logger.exception(exc)
    return JSONResponse(
        content={
            "error": {
                "error_msg": strings.unhandled_exception_text,
                "error_name": "unhandlederror",
                "error_payload": {},
            },
            "data": None
        },
        status_code=exc.status_code)


async def error_exception_handler(request: Request, exc: Exception):
    exception_info = f"Response: [{request.method}] -> {request.url} >>> {request.headers} <<<"
    logger.exception(f"{exception_info} Exception: {repr(exc)}")
    request_id = ""
    if hasattr(exc, "_request-id-for-response"):
        request_id = exc.__getattribute__("_request-id-for-response")

    await send_internal_exception_alarm(request, exc, request_id)

    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "error_msg": strings.unhandled_exception_text,
                "error_name": "",
                "error_payload": {}
            },
            "request_id": request_id,
            "data": None
        }
    )
