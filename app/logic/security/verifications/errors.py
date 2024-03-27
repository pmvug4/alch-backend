from core.exceptions.exception import AppHTTPException
from core.localization.data import error_add_localization


class EmailVerificationNotFound(AppHTTPException):
    status_code = 404
    error_name = 'email_verification_not_found'

    def __new__(cls, *args, **kwargs):
        super().__new__(*args, **kwargs)

        error_add_localization(
            cls.error_name,
            ru="Процесс верификации по email не найден.",
            en="Email verification process not found."
        )


class EmailVerificationRecheckIntervalNotPass(AppHTTPException):
    status_code = 400
    error_name = 'email_verification_retry_period_not_pass'

    def __new__(cls, *args, **kwargs):
        super().__new__(*args, **kwargs)

        error_add_localization(
            cls.error_name,
            ru="Время до следующей проверки еще не прошло, пожалуйста подождите и попробуйте позже.",
            en="The email verification recheck interval has not passed. Please try again later."
        )


class EmailVerificationAttemptsLeft(AppHTTPException):
    status_code = 410
    error_name = 'email_verification_attempts_left'

    def __new__(cls, *args, **kwargs):
        super().__new__(*args, **kwargs)

        error_add_localization(
            cls.error_name,
            ru="Попытки проверки кода закончились, пожалуйста запросите новый код.",
            en="The email verification failed. Please request a new code."
        )


class EmailVerificationIsInvalid(AppHTTPException):
    status_code = 410
    error_name = 'email_verification_is_invalid'

    def __new__(cls, *args, **kwargs):
        super().__new__(*args, **kwargs)

        error_add_localization(
            cls.error_name,
            ru="Проверка почты истекла, пожалуйста запросите новый код.",
            en="The email verification is no longer valid. Please request a new code."
        )


class IncorrectVerificationCode(AppHTTPException):
    status_code = 400
    error_name = 'incorrect_verification_code'

    def __new__(cls, *args, **kwargs):
        super().__new__(*args, **kwargs)

        error_add_localization(
            cls.error_name,
            ru="Неверный код подтверждения.",
            en="The verification code is incorrect."
        )


class VerificationNotYetVerified(AppHTTPException):
    status_code = 400
    error_name = 'verification_not_yet_verified'

    def __new__(cls, *args, **kwargs):
        super().__new__(*args, **kwargs)

        error_add_localization(
            cls.error_name,
            ru="Процесс верификации завершен некорректно.",
            en="The verification not yet verified."
        )
