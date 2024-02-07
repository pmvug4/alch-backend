from core.common import strings
from core.exception import AppHTTPException


class UserCreationError(AppHTTPException):
    # ошибко создания пользователя
    error_name = "unable_to_create_user"
    http_code = 400
    err_msg = strings.unable_to_create_user


class UserBulkCreationUniqueIndexError(AppHTTPException):
    error_name = 'user_bulk_creation_unique_index_error'
    http_code = 400
    err_msg = strings.user_name_is_busy

    @classmethod
    def build(cls, usernames: list[str]) -> 'UserBulkCreationUniqueIndexError':
        return cls(
            detail=f"{strings.unable_to_create_user}: {','.join(usernames)}"
        )
