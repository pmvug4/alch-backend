from core.exception import AppHTTPException
from core.common import strings


class PrivatePhotoInfoDoesNotExist(AppHTTPException):
    http_code = 400
    error_name = 'private_photo_info_does_not_exist'
    err_msg = strings.private_photo_info_does_not_exist
