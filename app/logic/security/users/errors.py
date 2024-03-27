from core.exceptions import AppHTTPException
from core.localization.data import error_add_localization


class UserNotFoundError(AppHTTPException):
    status_code = 404
    error_name = 'user_not_found'

    def __new__(cls, *args, **kwargs):
        super().__new__(*args, **kwargs)

        error_add_localization(
            cls.error_name,
            ru="Пользователь не найден.",
            en="User not found."
        )


class UserAlreadyExists(AppHTTPException):
    status_code = 409
    error_name = 'user_already_exists'

    def __new__(cls, *args, **kwargs):
        super().__new__(*args, **kwargs)

        error_add_localization(
            cls.error_name,
            ru="Пользователь с данным email уже существует.",
            en="User with this email already exists."
        )
