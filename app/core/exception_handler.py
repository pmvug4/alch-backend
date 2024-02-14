from typing import Union

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_422_UNPROCESSABLE_ENTITY

from core.common import strings
from core.config.internal import service_settings
from core.exception import AppHTTPException

from core.telegram import tg_send_alarm

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
                "error_name": "parse_data_error",
                "error_payload":
                    {
                        "validation_errors": exc.errors() if service_settings.RETURN_FULL_VALIDATION_ERRORS else ""
                    }
            },
            "data": None
        },
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
    )


async def http_handled_error_handler(request: Request, exc: AppHTTPException) -> JSONResponse:
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


async def http_unhandled_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    logger.exception(exc)
    return JSONResponse(
        content={
            "error": {
                "error_msg": strings.unhandled_exception_text,
                "error_name": "unhandled_error",
                "error_payload": {},
            },
            "data": None
        },
        status_code=exc.status_code
    )


async def http_internal_error_handler(request: Request, exc: Exception):
    exception_info = f"Response: [{request.method}] -> {request.url} >>> {request.headers} <<<"
    logger.exception(f"{exception_info} Exception: {repr(exc)}")
    request_id = ""
    if hasattr(exc, "_request-id-for-response"):
        request_id = exc.__getattribute__("_request-id-for-response")

    await tg_send_alarm(f"({request_id}) Internal error recorded: {repr(exc)}")

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
