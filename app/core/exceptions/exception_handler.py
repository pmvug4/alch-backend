from typing import Union

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_422_UNPROCESSABLE_ENTITY

from core.telegram import tg_send_alarm
from core.logs import log
from core.app_request import AppRequest

from .exception import AppHTTPException
from .schemas import ErrorModel


async def http422_error_handler(
        request: Request,
        exc: Union[RequestValidationError, ValidationError],
) -> JSONResponse:
    exception_info = f"Response: [{request.method}] -> {request.url} >>> {request.headers} <<<"
    log.exception(f"{exception_info}\nException: {repr(exc)}\n Body: {exc.body}")

    return JSONResponse(
        content={
            "error": ErrorModel.build_from_422(exc).dict(),
            "data": None
        },
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
    )


async def http_handled_error_handler(request: Request, exc: AppHTTPException) -> JSONResponse:
    exception_info = f"Response: [{request.method}] -> {request.url} "
    log.info(f"{exception_info} Exception: {repr(exc)}")

    return JSONResponse(
        content={
            "error": ErrorModel.build_from_app_http_exception(exc).dict(),
            "data": None
        },
        status_code=exc.status_code
    )


async def http_another_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    log.exception(exc)
    return JSONResponse(
        content={
            "error": ErrorModel.build_another_http_error().dict(),
            "data": None
        },
        status_code=exc.status_code
    )


async def http_internal_error_handler(request: Request, exc: Exception):
    exception_info = f"Response: [{request.method}] -> {request.url} >>> {request.headers} <<<"
    log.exception(f"{exception_info} Exception: {repr(exc)}")

    await tg_send_alarm(f"({AppRequest.id}) Internal error recorded: {repr(exc)}")

    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": ErrorModel.build_internal_error().dict(),
            "request_id": AppRequest.id,
            "data": None
        }
    )
