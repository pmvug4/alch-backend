from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ValidationError

from core.config.internal import service_settings
from core.exceptions.exception import AppHTTPException


class ErrorModel(BaseModel):
    name: str
    user_message: str
    payload: dict

    @classmethod
    def build_from_app_http_exception(cls, e: AppHTTPException) -> 'ErrorModel':
        return cls(
            name=e.error_name,
            user_message=e.user_message,
            payload=e.error_payload

        )

    @classmethod
    def build_from_422(cls, e: RequestValidationError | ValidationError) -> 'ErrorModel':
        return cls(
            name='parse_data_error',
            user_message='Request validation error',
            payload={
                'validation_errors': e.errors() if service_settings.RETURN_FULL_VALIDATION_ERRORS else None
            }
        )

    @classmethod
    def build_another_http_error(cls) -> 'ErrorModel':
        return cls(
            name='another_http_error',
            user_message='Another http error',
            payload={}
        )

    @classmethod
    def build_internal_error(cls) -> 'ErrorModel':
        return cls(
            name='internal_server_error',
            user_message='Internal server error',
            payload={}
        )
