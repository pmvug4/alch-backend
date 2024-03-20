from typing import Union

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError, BaseModel
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_422_UNPROCESSABLE_ENTITY

from core.config.internal import service_settings
from core.exception import AppHTTPException

from core.telegram import tg_send_alarm

from loguru import logger


class _ErrorModel(BaseModel):
    name: str
    user_message: str
    payload: dict

    @classmethod
    def build_from_app_http_exception(cls, e: AppHTTPException) -> '_ErrorModel':
        return cls(
            name=e.error_name,
            user_message=e.user_message,
            payload=e.error_payload

        )

    @classmethod
    def build_from_422(cls, e: RequestValidationError | ValidationError) -> '_ErrorModel':
        return cls(
            name='parse_data_error',
            user_message='Request validation error',
            payload={
                'validation_errors': e.errors() if service_settings.RETURN_FULL_VALIDATION_ERRORS else None
            }
        )

    @classmethod
    def build_another_http_error(cls) -> '_ErrorModel':
        return cls(
            name='another_http_error',
            user_message='Another http error',
            payload={}
        )

    @classmethod
    def build_internal_error(cls) -> '_ErrorModel':
        return cls(
            name='internal_server_error',
            user_message='Internal server error',
            payload={}
        )


async def http422_error_handler(
        request: Request,
        exc: Union[RequestValidationError, ValidationError],
) -> JSONResponse:
    exception_info = f"Response: [{request.method}] -> {request.url} >>> {request.headers} <<<"
    logger.exception(f"{exception_info}\nException: {repr(exc)}\n Body: {exc.body}")

    return JSONResponse(
        content={
            "error": _ErrorModel.build_from_422(exc).dict(),
            "data": None
        },
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
    )


async def http_handled_error_handler(request: Request, exc: AppHTTPException) -> JSONResponse:
    exception_info = f"Response: [{request.method}] -> {request.url} "
    logger.info(f"{exception_info} Exception: {repr(exc)}")

    return JSONResponse(
        content={
            "error": _ErrorModel.build_from_app_http_exception(exc).dict(),
            "data": None
        },
        status_code=exc.status_code
    )


async def http_another_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    logger.exception(exc)
    return JSONResponse(
        content={
            "error": _ErrorModel.build_another_http_error().dict(),
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
            "error": _ErrorModel.build_internal_error().dict(),
            "request_id": request_id,
            "data": None
        }
    )
