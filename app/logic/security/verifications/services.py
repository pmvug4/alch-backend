import datetime
import random
from uuid import UUID

from databases.core import Connection, Database

from pydantic import EmailStr

from core.config.internal import auth_settings

from .models import EmailVerification, EmailVerificationForm
from .store import EmailVerificationStore
from .errors import (
    EmailVerificationRecheckIntervalNotPass,
    EmailVerificationAttemptsLeft,
    EmailVerificationIsInvalid,
    IncorrectVerificationCode,
    VerificationNotYetVerified
)
from .telegram import send_email_code


class EmailVerificationService:
    @staticmethod
    async def start_verification(
            conn: Connection | Database,
            email: EmailStr
    ) -> EmailVerification:
        async with conn.transaction():
            store = EmailVerificationStore(conn)

            _size = auth_settings.AUTH_OTP_PASSWORD_LENGTH
            _attempts = auth_settings.AUTH_OTP_PASSWORD_CHECKS
            _valid_interval = auth_settings.AUTH_OTP_PASSWORD_VALID_PERIOD_SECONDS

            if not await store.check_next_avail(
                    email=email,
                    min_interval_s=auth_settings.AUTH_OTP_RETRY_PERIOD_SECONDS
            ):
                raise EmailVerificationRecheckIntervalNotPass

            code = str(random.randint(1, 10**_size - 1)).zfill(_size)

            await send_email_code(
                email=email,
                code=code
            )

            return await store.create(
                EmailVerificationForm(
                    email=email,
                    code=code,
                    attempts_left=_attempts,
                    valid_until=datetime.datetime.now() + datetime.timedelta(seconds=_valid_interval)
                )
            )

    @staticmethod
    async def complete_verification(
            conn: Connection | Database,
            key: UUID,
            code: str
    ) -> EmailVerification:
        async with conn.transaction():
            store = EmailVerificationStore(conn)

            email_verification = await store.get(
                key=key,
                for_update=True,
                return_none=False
            )

            if not email_verification.attempts_left:
                raise EmailVerificationAttemptsLeft
            elif email_verification.valid_until < datetime.datetime.now():
                raise EmailVerificationIsInvalid

            if email_verification.code != code:
                await store.remove_attempt(email_verification.id)
                # raise After transaction commitment
            else:
                return await store.mark_verified(email_verification.id)

        raise IncorrectVerificationCode

    @staticmethod
    async def validate_verified(
            conn: Connection | Database,
            key: UUID
    ) -> EmailVerification:
        email_verification = await EmailVerificationStore(conn).get(key=key)

        if not email_verification.verified:
            raise VerificationNotYetVerified
        elif email_verification.valid_until < datetime.datetime.now():
            raise EmailVerificationIsInvalid

        return email_verification
