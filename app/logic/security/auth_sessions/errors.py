from core.exceptions import AppHTTPException
from core.localization.data import error_add_localization


class AuthSessionNotFoundError(AppHTTPException):
    status_code = 404
    error_name = 'auth_session_not_found'

    def __new__(cls, *args, **kwargs):
        super().__new__(*args, **kwargs)

        error_add_localization(
            cls.error_name,
            ru="Сессия авторизации не найдена.",
            en="Authorization session not found."
        )


class WrongAuthSessionRefreshToken(AppHTTPException):
    status_code = 403
    error_name = 'wrong_auth_session_refresh_token'

    def __new__(cls, *args, **kwargs):
        super().__new__(*args, **kwargs)

        error_add_localization(
            cls.error_name,
            ru="Упс..., ваша сессия устарела, пожалуйста, перезайдите в свой аккаунт.",
            en="Oops..., your authorization session is expired, please re-login in your account."
        )
