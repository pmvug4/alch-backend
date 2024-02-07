from core.exception import AppHTTPException
from core.common import strings


class NotificationAccessDenied(AppHTTPException):
    http_code = 403
    error_name = 'notification_access_denied'
    err_msg = strings.notification_access_denied


class NotificationDoesNotExist(AppHTTPException):
    http_code = 400
    error_name = 'notification_does_not_exist'
    err_msg = strings.notification_does_not_exist
