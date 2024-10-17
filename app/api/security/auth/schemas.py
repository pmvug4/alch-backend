from pydantic import BaseModel, EmailStr, field_validator, constr
from uuid import UUID

from logic.security.auth_sessions import AuthSessionPlatformNames


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    group_id: int = 1
    platform: AuthSessionPlatformNames

    @field_validator('email', 'password')
    @classmethod
    def _validate_length(cls, value: str) -> str:
        if len(value) > 127:
            raise ValueError('Max len is 127')

        return value


class StartEmailVerificationRequest(BaseModel):
    email: EmailStr

    @field_validator('email')
    @classmethod
    def _validate_length(cls, value: str) -> str:
        if len(value) > 127:
            raise ValueError('Max len is 127')

        return value


class CompleteEmailVerificationRequest(BaseModel):
    key: UUID
    code: constr(max_length=7)


class RegisterAccountRequest(BaseModel):
    email_verification_key: UUID
    password: constr(max_length=127)
