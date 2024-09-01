from core.exceptions import AppHTTPException
from core.localization.data import error_add_localization


class PlayerNotFoundError(AppHTTPException):
    status_code = 404
    error_name = 'player_not_found'

    error_add_localization(
        error_name,
        ru="Игрок не найден.",
        en="Player not found."
    )


class PlayerUniqueError(AppHTTPException):
    status_code = 409
    error_name = 'player_unique_error'

    error_add_localization(
        error_name,
        ru="Ошибка создания игрока, попробуйте еще раз",
        en="Player creation error, please try again."
    )
