from core.exceptions import AppHTTPException
from core.localization.data import error_add_localization


class PlayerBalanceNotFoundError(AppHTTPException):
    status_code = 404
    error_name = 'player_balance_not_found'

    error_add_localization(
        error_name,
        ru="Игрок не найден.",
        en="Player not found."
    )


class PlayerBalanceUniqueError(AppHTTPException):
    status_code = 409
    error_name = 'player_balance_unique_error'

    error_add_localization(
        error_name,
        ru="Ошибка с созданием профиля, попробуйте еще раз.",
        en="Player creation error, please try again."
    )
