from typing import Optional, Dict, Any

from fastapi import HTTPException
from pydantic import create_model

from core import localization
from core.localization.data import error_add_localization
from core.app_request import AppRequest


class AppHTTPException(HTTPException):
    status_code = 400
    error_name = "base_error"

    _model = None

    @classmethod
    def get_model(cls):
        if not cls._model:
            cls._model = create_model(
                cls.__name__,
                error_name=cls.error_name,
                error_payload=(dict, dict())
            )

        return cls._model

    def __init__(
            self,
            status_code: int = None,
            lang: localization.Language | str = None,
            msg_format: dict = None,
            msg_override: str = None,
            extra_headers: Dict[str, Any] = None,
            error_payload: Dict[str, Any] = None
    ) -> None:
        super().__init__(
            status_code=status_code or self.status_code,
            detail='',
            headers=extra_headers
        )

        self.status_code: int = self.status_code
        self.error_name: str = type(self).error_name

        self.lang: localization.Language | str = lang or AppRequest.lang.get()
        self.extra_headers: dict = extra_headers or {}
        self.error_payload: dict = error_payload or {}
        self.msg_format: Optional[dict] = msg_format
        self.msg_override: Optional[str] = msg_override

    @property
    def user_message(self) -> str:
        if self.msg_override:
            return self.msg_override
        else:
            return localization.get_text(
                f'error__{self.error_name}',
                lang=self.lang,
                default='Error was happened.'
            ).format(
                **self.msg_format
            )


class IncorrectCredentials(AppHTTPException):
    # общая ошибка авторизации, нет пользователя или пароль неверный ошибка декодирования jwt и т.п.
    error_name = "incorrect_credentials"
    status_code = 401

    def __new__(cls, *args, **kwargs):
        super().__new__(*args, **kwargs)

        error_add_localization(
            cls.error_name,
            ru="Произошла ошибка авторизации, пожалуйста перезайдите в приложение.",
            en="Authorization error was happened, please re-login into the app."
        )


class AccessTokenExpired(AppHTTPException):
    error_name = "access_token_expired"
    status_code = 401

    def __new__(cls, *args, **kwargs):
        super().__new__(*args, **kwargs)

        error_add_localization(
            cls.error_name,
            ru="Произошла ошибка авторизации, пожалуйста перезайдите в приложение.",
            en="Authorization error was happened, please re-login into the app."
        )


class AccessForbidden(AppHTTPException):
    error_name = "access_forbidden"
    status_code = 403

    def __new__(cls, *args, **kwargs):
        super().__new__(*args, **kwargs)

        error_add_localization(
            cls.error_name,
            ru="Доступ к данному ресурсу запрещен.",
            en="Access forbidden."
        )


class NotDevelopedError(AppHTTPException):
    error_name = 'not_developed_error'
    status_code = 418


class RaceConditionError(AppHTTPException):
    status_code = 400
    error_name = 'race_condition_error'
