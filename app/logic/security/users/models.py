from typing import Optional
from pydantic import BaseModel, EmailStr
from uuid import UUID
import datetime


class PresignUserForm(BaseModel):
    group_id: int


class UserView(BaseModel):
    id: int
    uuid: UUID
    group_id: int
    email: Optional[EmailStr]

    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime]
    deleted_at: Optional[datetime.datetime]


class User(UserView):
    password_hash: Optional[str]
