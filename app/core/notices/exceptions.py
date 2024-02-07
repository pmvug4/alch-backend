from core.common import strings
from core.exception import AppHTTPException


class NewsDoesNotExist(Exception):
    pass


class NoticeReceiverDoesNotExist(Exception):
    pass


class NotificationDoesNotExist(Exception):
    pass


class NotificationAccessDenied(Exception):
    pass


class WrongReceiverID(Exception):
    pass


class BulkNotificationReceiverIdsDontMatchUserGroup(AppHTTPException):
    error_name = "bulk_notification_receiver_ids_dont_match_user_group"
    http_code = 400
    err_msg = strings.bulk_notification_receiver_ids_dont_match_user_group


class BulkNotificationDoesNotExist(AppHTTPException):
    error_name = "bulk_notification_does_not_exist"
    http_code = 404
    err_msg = strings.bulk_notification_does_not_exist
