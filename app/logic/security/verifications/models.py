import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr


class EmailVerificationForm(BaseModel):
    email: EmailStr
    code: str
    attempts_left: int
    valid_until: datetime.datetime


class EmailVerification(EmailVerificationForm):
    id: int
    key: UUID
    verified: bool
    created_at: datetime.datetime
