import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, validator, ValidationError, constr, EmailStr

from core.models import phone_regex


class AuthResponse(BaseModel):
    user_id: int
    access_token: str
    token_type: str
    refresh_token: str


class AuthOTP(BaseModel):
    username: constr(regex=phone_regex)
    password: str


class RefreshToken(BaseModel):
    refresh_token: str
    user_id: int
    user_uuid: Optional[UUID]

    @validator('refresh_token')
    def not_null(cls, v):
        if not v:
            raise ValidationError("refresh_token must be non empty")
        return v


class DeliveryFrequency(str, Enum):
    one_time = 'one_time'
    regular = 'regular'


class CustomerLeadForm(BaseModel):
    uuid: str
    email: EmailStr
    phone: constr(regex=phone_regex)
    company_name: str
    name: str
    delivery_frequency: DeliveryFrequency


class CustomerLead(CustomerLeadForm):
    id: int
    ctime: datetime.datetime


class CourierLeadForm(BaseModel):
    uuid: str
    email: EmailStr
    phone: constr(regex=phone_regex)
    first_name: str
    last_name: str = None
    question: str = None
    have_licence: bool | None


class CourierLead(CourierLeadForm):
    id: int
    ctime: datetime.datetime
