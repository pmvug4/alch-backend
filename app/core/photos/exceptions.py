from core.common import strings
from core.exception import AppHTTPException


class PhotoDoesNotExist(AppHTTPException):
    http_code = 400
    error_name = 'photo_does_not_exist'
    err_msg = strings.photo_does_not_exist


class WrongPhotoType(Exception):
    pass


class UnexpectedPhotoExtension(AppHTTPException):
    http_code = 400
    error_name = 'unexpected_photo_extension'
    err_msg = strings.unexpected_photo_extension


class PhotoNotInList(AppHTTPException):
    http_code = 400
    error_name = 'photo_not_in_list'
    err_msg = strings.photo_not_in_list
