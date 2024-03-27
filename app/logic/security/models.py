import datetime
from pydantic import BaseModel
from uuid import UUID


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: UUID
    session_uuid: UUID


class EmailVerificationResponse(BaseModel):
    key: UUID
    verified: bool
    attempts_left: int
    valid_until: datetime.datetime
