from typing import Optional, Dict, Any

from fastapi import HTTPException
from pydantic import create_model

from core.common import strings


class AppHTTPException(HTTPException):
    error_name = "base_error"
    http_code = 400
    err_msg = "Error occurred"
    model = None

    def __init__(
            self,
            status_code: int = None,
            detail: Any = None,
            headers: Optional[Dict[str, Any]] = None,
            error_payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        _status_code = status_code or self.http_code
        _msg = detail or self.err_msg
        super().__init__(status_code=_status_code, detail=_msg, headers=headers)
        self.headers = headers
        self.error_payload = error_payload or dict()

    @classmethod
    def get_model(cls):
        if not cls.model:
            cls.model = create_model(cls.__name__,
                                     error_msg=cls.err_msg,
                                     error_name=cls.error_name,
                                     error_payload=(dict, dict()))
        return cls.model


class IncorrectCredentials(AppHTTPException):
    # общая ошибка авторизации, нет пользователя или пароль неверный ошибка декодирования jwt и т.п.
    error_name = "incorrect_credentials"
    http_code = 401
    err_msg = strings.auth_error


class AppZoneIsExpired(AppHTTPException):
    error_name = 'app_zone_is_expired'
    http_code = 401
    err_msg = strings.app_zone_is_expired


class AccessTokenExpired(AppHTTPException):
    error_name = "access_token_expired"
    http_code = 401
    err_msg = strings.auth_token_expired


class AccessForbidden(AppHTTPException):
    # доступ к данным запрещен
    error_name = "access_forbidden"
    http_code = 403
    err_msg = strings.access_forbidden


class NotDevelopedError(AppHTTPException):
    error_name = 'not_developed_error'
    http_code = 418
    err_msg = strings.not_developed_error


class RaceConditionError(AppHTTPException):
    http_code = 400
    error_name = 'race_condition_error'
    err_msg = strings.race_condition_error
