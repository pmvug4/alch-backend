from pydantic import BaseModel, EmailStr, validator, constr
from uuid import UUID

from logic.security.auth_sessions import AuthSessionPlatformNames


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    group_id: int = 1
    platform: AuthSessionPlatformNames

    @validator('email', 'password')
    def _validate_length(self, value: str) -> str:
        if len(value) > 127:
            raise ValueError('Max len is 127')

        return value


class StartEmailVerificationRequest(BaseModel):
    email: EmailStr

    @validator('email')
    def _validate_length(self, value: str) -> str:
        if len(value) > 127:
            raise ValueError('Max len is 127')

        return value


class CompleteEmailVerificationRequest(BaseModel):
    key: UUID
    code: constr(max_length=7)


class RegisterAccountRequest(BaseModel):
    email_verification_key: UUID
    password: constr(max_length=127)
