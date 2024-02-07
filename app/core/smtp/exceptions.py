from core.exception import AppHTTPException
from core.common import strings


class UnexpectedSmtpExtension(AppHTTPException):
    http_code = 400
    error_name = 'unexpected_smtp_extension'
    err_msg = strings.unexpected_smtp_extension
