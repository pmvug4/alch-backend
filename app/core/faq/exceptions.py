from core.exception import AppHTTPException
from core.common import strings


class FaqIsNotExist(AppHTTPException):
    http_code = 400
    error_name = 'faq_is_not_exist'
    err_msg = strings.faq_is_not_exist


class FaqAccessDenied(AppHTTPException):
    http_code = 403
    error_name = 'faq_access_denied'
    err_msg = strings.faq_access_denied
