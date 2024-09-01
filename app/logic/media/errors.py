from core.exceptions import AppHTTPException
from core.localization.data import error_add_localization


class MediaNotFoundError(AppHTTPException):
    status_code = 404
    error_name = 'media_not_found'

    error_add_localization(
        error_name,
        ru="Медиа файл не найден.",
        en="Media not found."
    )


class MediaUniqueError(AppHTTPException):
    status_code = 409
    error_name = 'media_unique_error'

    error_add_localization(
        error_name,
        ru="Ошибка загрузки медиа-файла, попробуйте еще раз",
        en="Media uploading error, please try again."
    )
