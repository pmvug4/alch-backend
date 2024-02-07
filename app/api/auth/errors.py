from core.common import strings
from core.exception import AppHTTPException


class IncorrectOTPPassword(AppHTTPException):
    # не корректный OTP пароль
    error_name = "incorrect_otp_password"
    http_code = 401
    err_msg = strings.auth_otp_incorrect_password


class IncorrectPhoneNumber(AppHTTPException):
    # не корректный номер телефона
    error_name = "incorrect_phone_number"
    http_code = 401
    err_msg = strings.auth_otp_incorrect_phone_number


class UnknownSmsSendingError(AppHTTPException):
    # неизвестная ошибка отправки смс
    error_name = "unknown_sms_sending_error"
    http_code = 401
    err_msg = strings.unknown_sms_exception_text


class UnknownCallSendingError(AppHTTPException):
    # неизвестная ошибка отправки звонка
    error_name = "unknown_call_sending_error"
    http_code = 401
    err_msg = strings.unknown_call_exception_text


class UnknownVerificationCodeError(AppHTTPException):
    # неизвестная ошибка отправки кода верификации
    error_name = "unknown_verification_code_error"
    http_code = 401
    err_msg = strings.unknown_verification_code_error


class NeedNewOTPPassword(AppHTTPException):
    # исчерпан лимит проверки отправленного пароля
    error_name = "opt_password_checks_exhaused"
    http_code = 401
    err_msg = strings.auth_otp_checks_exhausted


class OTPPasswordResendIntervalNotPass(AppHTTPException):
    # не прошел интервал для повторного запроса пароля
    error_name = "opt_password_interval_not_pass"
    http_code = 400
    err_msg = strings.auth_otp_interval


class OTPPasswordSendError(AppHTTPException):
    # возникла ошибка при оправке OTP пароля
    error_name = "opt_password_send_error"
    http_code = 400
    err_msg = strings.auth_otp_send_fail


class InvalidRefreshToken(AppHTTPException):
    # получен не валидный refresh токен
    error_name = "invalid_refresh_token"
    http_code = 401
    err_msg = strings.auth_error


class OTPAuthForbidden(AppHTTPException):
    # авторизация с помощью OTP запрещена
    error_name = "otp_forbiden"
    http_code = 401
    err_msg = strings.auth_otp_forbidden


class UserNameIsBusy(AppHTTPException):
    # пользователь с таким номером телефона уже существует
    error_name = "user_name_is_busy"
    http_code = 400
    err_msg = strings.user_name_is_busy


class LeadAlreadyExists(AppHTTPException):
    error_name = "lead_already_exist"
    http_code = 400
    err_msg = strings.lead_already_exist
